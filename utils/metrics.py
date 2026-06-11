"""
Metrics calculation module for Somalia Market Intelligence Platform.
Computes KPIs, health scores, volatility, and correlation statistics.
"""

from typing import Dict, Tuple

import numpy as np
import pandas as pd


def get_latest_exchange_rate(df: pd.DataFrame) -> Tuple[float, float]:
    """
    Return the most recent USD/SOS rate and its change from the prior month.

    Args:
        df: Exchange rates DataFrame with 'date' and 'usd_sos' columns.

    Returns:
        (latest_rate, monthly_change)
    """
    df_sorted = df.sort_values("date")
    latest = df_sorted["usd_sos"].iloc[-1]
    prev = df_sorted["usd_sos"].iloc[-2] if len(df_sorted) >= 2 else latest
    return round(latest, 2), round(latest - prev, 2)


def get_latest_commodity_summary(df: pd.DataFrame) -> Dict:
    """
    Compute the average commodity price and average month-on-month change.

    Returns:
        dict with keys: avg_price, avg_change
    """
    df_sorted = df.sort_values("date")
    latest_prices = df_sorted.groupby("commodity").tail(1)
    prev_prices = df_sorted.groupby("commodity").nth(-2)

    avg_price = latest_prices["price_usd"].mean()

    if len(prev_prices) > 0:
        merged = latest_prices.set_index("commodity")[["price_usd"]].join(
            prev_prices.set_index("commodity")[["price_usd"]],
            rsuffix="_prev",
        )
        merged = merged.dropna()
        if len(merged) > 0:
            merged["pct_change"] = (
                (merged["price_usd"] - merged["price_usd_prev"])
                / merged["price_usd_prev"]
            ) * 100
            avg_change = merged["pct_change"].mean()
        else:
            avg_change = 0.0
    else:
        avg_change = 0.0

    return {"avg_price": round(avg_price, 3), "avg_change": round(avg_change, 2)}


def get_latest_fuel_summary(df: pd.DataFrame) -> Dict:
    """
    Compute the average fuel price and average month-on-month change.

    Returns:
        dict with keys: avg_price, avg_change
    """
    df_sorted = df.sort_values("date")
    latest = df_sorted.groupby("fuel_type").tail(1)
    prev = df_sorted.groupby("fuel_type").nth(-2)

    avg_price = latest["price_usd"].mean()

    if len(prev) > 0:
        merged = latest.set_index("fuel_type")[["price_usd"]].join(
            prev.set_index("fuel_type")[["price_usd"]], rsuffix="_prev"
        )
        merged = merged.dropna()
        if len(merged) > 0:
            merged["pct_change"] = (
                (merged["price_usd"] - merged["price_usd_prev"])
                / merged["price_usd_prev"]
            ) * 100
            avg_change = merged["pct_change"].mean()
        else:
            avg_change = 0.0
    else:
        avg_change = 0.0

    return {"avg_price": round(avg_price, 3), "avg_change": round(avg_change, 2)}


# ── Health score helpers ───────────────────────────────────────────────────────

def _lerp_score(cv_pct: float, low_cv: float, high_cv: float, max_pts: int) -> int:
    """
    Map a Coefficient of Variation (as a percentage) to a score via linear
    interpolation.  Full marks when cv_pct ≤ low_cv; zero when cv_pct ≥ high_cv.

    Args:
        cv_pct:  Measured CV expressed as a percentage (e.g. 2.3, not 0.023).
        low_cv:  CV threshold below which full marks are awarded.
        high_cv: CV threshold at or above which zero marks are awarded.
        max_pts: Maximum possible points for this component.

    Returns:
        Integer score in [0, max_pts].
    """
    if cv_pct <= low_cv:
        return max_pts
    if cv_pct >= high_cv:
        return 0
    fraction = (cv_pct - low_cv) / (high_cv - low_cv)
    return round(max_pts * (1.0 - fraction))


def _stability_label(score: int, max_pts: int) -> str:
    """Return a human-readable stability label based on the fraction of max points."""
    pct = score / max_pts if max_pts > 0 else 0.0
    if pct >= 0.75:
        return "Stable"
    elif pct >= 0.45:
        return "Moderate"
    else:
        return "Elevated"


def _overall_label(total: int) -> str:
    if total >= 65:
        return "Stable"
    elif total >= 40:
        return "Moderate"
    else:
        return "Elevated Risk"


# ── Market health score ────────────────────────────────────────────────────────

def get_market_health_breakdown(
    df_exchange: pd.DataFrame,
    df_commodity: pd.DataFrame,
    df_fuel: pd.DataFrame,
) -> Dict:
    """
    Compute a composite market health score (0–100) with a full component breakdown.

    Methodology
    -----------
    Three components are scored using linear interpolation between a "stable"
    threshold (full marks) and a "stressed" threshold (zero marks).  Both
    thresholds are calibrated to Somalia's historical market conditions.

    Exchange rate stability — 30 pts
        Metric : 3-month rolling CV of USD/SOS rate (last 3 observations).
        Full marks : CV ≤ 0.10 %  (rate barely moving)
        Zero marks : CV ≥ 0.70 %  (rate swinging ≥ 4 SOS/month)

    Commodity price stability — 40 pts
        Metric : mean 24-month CV across all tracked commodities.
        Full marks : avg CV ≤ 1.5 %
        Zero marks : avg CV ≥ 12.0 %

    Fuel price stability — 30 pts
        Metric : mean 24-month CV across fuel types.
        Full marks : avg CV ≤ 1.5 %
        Zero marks : avg CV ≥ 10.0 %

    Returns
    -------
    dict with keys:
        total          : int (0–100)
        overall_label  : str ("Stable" / "Moderate" / "Elevated Risk")
        exchange_rate  : {score, max, cv_pct, label}
        commodity      : {score, max, cv_pct, label}
        fuel           : {score, max, cv_pct, label}
    """
    # --- Exchange rate component (30 pts) ---
    if len(df_exchange) >= 3:
        recent_ex = df_exchange.sort_values("date").tail(3)["usd_sos"]
        cv_ex_pct = float(
            recent_ex.std() / recent_ex.mean() * 100
        ) if recent_ex.mean() > 0 else 0.0
    else:
        cv_ex_pct = 0.0
    ex_score = _lerp_score(cv_ex_pct, low_cv=0.10, high_cv=0.70, max_pts=30)

    # --- Commodity component (40 pts) ---
    if len(df_commodity) > 0:
        cv_per_com = df_commodity.groupby("commodity")["price_usd"].agg(
            lambda s: float(s.std() / s.mean() * 100) if s.mean() > 0 else 0.0
        )
        avg_cv_com_pct = float(cv_per_com.mean())
    else:
        avg_cv_com_pct = 0.0
    com_score = _lerp_score(avg_cv_com_pct, low_cv=1.5, high_cv=12.0, max_pts=40)

    # --- Fuel component (30 pts) ---
    if len(df_fuel) > 0:
        cv_per_fuel = df_fuel.groupby("fuel_type")["price_usd"].agg(
            lambda s: float(s.std() / s.mean() * 100) if s.mean() > 0 else 0.0
        )
        avg_cv_fuel_pct = float(cv_per_fuel.mean())
    else:
        avg_cv_fuel_pct = 0.0
    fuel_score = _lerp_score(avg_cv_fuel_pct, low_cv=1.5, high_cv=10.0, max_pts=30)

    total = min(100, max(0, ex_score + com_score + fuel_score))

    return {
        "total": total,
        "overall_label": _overall_label(total),
        "exchange_rate": {
            "score": ex_score,
            "max": 30,
            "cv_pct": round(cv_ex_pct, 3),
            "label": _stability_label(ex_score, 30),
        },
        "commodity": {
            "score": com_score,
            "max": 40,
            "cv_pct": round(avg_cv_com_pct, 2),
            "label": _stability_label(com_score, 40),
        },
        "fuel": {
            "score": fuel_score,
            "max": 30,
            "cv_pct": round(avg_cv_fuel_pct, 2),
            "label": _stability_label(fuel_score, 30),
        },
    }


def get_market_health_score(
    df_exchange: pd.DataFrame,
    df_commodity: pd.DataFrame,
    df_fuel: pd.DataFrame,
) -> int:
    """Return only the integer total from get_market_health_breakdown (backward compat)."""
    return get_market_health_breakdown(df_exchange, df_commodity, df_fuel)["total"]


# ── Price change statistics ────────────────────────────────────────────────────

def calculate_price_changes(df: pd.DataFrame, price_col: str, group_col: str) -> pd.DataFrame:
    """
    Calculate price statistics per group (commodity or fuel type).

    Args:
        df: Price DataFrame sorted by date.
        price_col: Column name for prices.
        group_col: Column to group by (e.g. 'commodity').

    Returns:
        DataFrame with latest price, 1-month change, 3-month change, YTD change,
        and coefficient of variation for each group.
    """
    df_sorted = df.sort_values("date")
    results = []

    for group, gdf in df_sorted.groupby(group_col):
        gdf = gdf.sort_values("date").reset_index(drop=True)
        latest = gdf[price_col].iloc[-1]

        prev_1m = gdf[price_col].iloc[-2] if len(gdf) >= 2 else latest
        prev_3m = gdf[price_col].iloc[-4] if len(gdf) >= 4 else gdf[price_col].iloc[0]
        prev_ytd = gdf[price_col].iloc[0]

        chg_1m = round((latest - prev_1m) / prev_1m * 100, 2) if prev_1m else 0
        chg_3m = round((latest - prev_3m) / prev_3m * 100, 2) if prev_3m else 0
        chg_ytd = round((latest - prev_ytd) / prev_ytd * 100, 2) if prev_ytd else 0
        cv = round(gdf[price_col].std() / gdf[price_col].mean() * 100, 2) if gdf[price_col].mean() > 0 else 0

        results.append(
            {
                group_col: group,
                "latest_price": round(latest, 3),
                "change_1m_pct": chg_1m,
                "change_3m_pct": chg_3m,
                "change_ytd_pct": chg_ytd,
                "volatility_cv": cv,
            }
        )

    return pd.DataFrame(results)


def calculate_commodity_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a price correlation matrix across all commodities.

    Args:
        df: Commodity prices DataFrame.

    Returns:
        Correlation matrix as a DataFrame.
    """
    pivot = df.pivot_table(index="date", columns="commodity", values="price_usd")
    return pivot.corr().round(3)


def get_trend_label(change_pct: float) -> str:
    """Return a human-readable trend label based on percentage change."""
    if change_pct > 5:
        return "Strong Increase"
    elif change_pct > 2:
        return "Moderate Increase"
    elif change_pct > 0:
        return "Slight Increase"
    elif change_pct > -2:
        return "Stable"
    elif change_pct > -5:
        return "Slight Decrease"
    else:
        return "Strong Decrease"
