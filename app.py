"""
Somalia Market Intelligence & Price Monitoring Platform
========================================================
Main entry point — Dashboard page.

Run with:
    streamlit run app.py

Requires Python 3.11+ and the packages listed in requirements.txt.
No environment variables, external APIs, or paid services needed.
"""

import os
import sys

# Ensure utils/ and pages/ are importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from utils.database import initialize_database
from utils.loaders import load_commodity_prices, load_exchange_rates, load_fuel_prices
from utils.charts import (
    create_commodity_overview_chart,
    create_exchange_rate_chart,
    create_fuel_overview_chart,
)
from utils.metrics import (
    get_latest_commodity_summary,
    get_latest_exchange_rate,
    get_latest_fuel_summary,
    get_market_health_breakdown,
)

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Somalia Market Intelligence",
    page_icon="🇸🇴",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/",
        "About": "Somalia Market Intelligence & Price Monitoring Platform v1.0",
    },
)


@st.cache_data(ttl=300)
def load_all_data():
    """Load and cache all market datasets."""
    return (
        load_exchange_rates(),
        load_commodity_prices(),
        load_fuel_prices(),
    )


def render_sidebar_info() -> None:
    """Render informational sidebar content."""
    with st.sidebar:
        st.markdown("## 🇸🇴 Somalia MIP")
        st.markdown(
            "**Market Intelligence & Price Monitoring Platform**  \n"
            "Tracking exchange rates, commodities, and fuel across Somalia."
        )
        st.divider()
        st.markdown("### Navigation")
        st.markdown(
            "Use the pages above to explore:\n"
            "- 📈 **Exchange Rates** — USD/SOS trends\n"
            "- 🌾 **Commodity Prices** — Food basket tracking\n"
            "- ⛽ **Fuel Prices** — Diesel & Petrol trends\n"
            "- 📊 **Analytics** — Volatility & correlations"
        )
        st.divider()
        st.caption("Data: REER Market Survey | Mogadishu | 2023–2024")


def render_kpi_row(df_ex, df_com, df_fuel) -> None:
    """Render the top KPI metric cards."""
    latest_rate, rate_change = get_latest_exchange_rate(df_ex)
    breakdown = get_market_health_breakdown(df_ex, df_com, df_fuel)
    health_score = breakdown["total"]
    com_summary = get_latest_commodity_summary(df_com)
    fuel_summary = get_latest_fuel_summary(df_fuel)

    n_indicators = (
        df_com["commodity"].nunique()
        + df_fuel["fuel_type"].nunique()
        + 1  # exchange rate
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="📌 Tracked Indicators",
            value=str(n_indicators),
            delta="Active",
        )
    with col2:
        st.metric(
            label="💱 USD / SOS Rate",
            value=f"{latest_rate:,.2f}",
            delta=f"{rate_change:+.2f} SOS",
            delta_color="inverse",
        )
    with col3:
        st.metric(
            label="🌾 Avg Commodity Price",
            value=f"${com_summary['avg_price']:.3f}",
            delta=f"{com_summary['avg_change']:+.2f}% MoM",
            delta_color="inverse",
        )
    with col4:
        st.metric(
            label="⛽ Avg Fuel Price",
            value=f"${fuel_summary['avg_price']:.3f}/L",
            delta=f"{fuel_summary['avg_change']:+.2f}% MoM",
            delta_color="inverse",
        )
    with col5:
        st.metric(
            label="🏥 Market Health Score",
            value=f"{health_score} / 100",
            delta=breakdown["overall_label"],
        )

    return breakdown


def render_health_breakdown(breakdown: dict) -> None:
    """Render an expandable component breakdown of the Market Health Score."""
    with st.expander("📊 Market Health Score — Component Breakdown", expanded=False):
        st.markdown(
            "The score is a weighted composite of three stability indicators, "
            "each measured by the **Coefficient of Variation (CV%)** of prices "
            "over the tracking period. Lower volatility → higher score."
        )
        st.divider()

        col1, col2, col3 = st.columns(3)

        ex = breakdown["exchange_rate"]
        com = breakdown["commodity"]
        fuel = breakdown["fuel"]

        _label_icon = {"Stable": "🟢", "Moderate": "🟡", "Elevated": "🔴"}

        with col1:
            st.markdown("#### 💱 Exchange Rate Stability")
            st.metric(
                label="Score",
                value=f"{ex['score']} / {ex['max']}",
                delta=f"{_label_icon.get(ex['label'], '')} {ex['label']}",
            )
            st.caption(
                f"**Metric:** 3-month rolling CV of USD/SOS  \n"
                f"**Measured CV:** {ex['cv_pct']:.3f}%  \n"
                f"**Thresholds:** ≤ 0.10% → full marks · ≥ 0.70% → zero  \n"
                f"**Weight:** 30 pts"
            )

        with col2:
            st.markdown("#### 🌾 Commodity Price Stability")
            st.metric(
                label="Score",
                value=f"{com['score']} / {com['max']}",
                delta=f"{_label_icon.get(com['label'], '')} {com['label']}",
            )
            st.caption(
                f"**Metric:** Mean 24-month CV across all commodities  \n"
                f"**Measured CV:** {com['cv_pct']:.2f}%  \n"
                f"**Thresholds:** ≤ 1.5% → full marks · ≥ 12.0% → zero  \n"
                f"**Weight:** 40 pts"
            )

        with col3:
            st.markdown("#### ⛽ Fuel Price Stability")
            st.metric(
                label="Score",
                value=f"{fuel['score']} / {fuel['max']}",
                delta=f"{_label_icon.get(fuel['label'], '')} {fuel['label']}",
            )
            st.caption(
                f"**Metric:** Mean 24-month CV across fuel types  \n"
                f"**Measured CV:** {fuel['cv_pct']:.2f}%  \n"
                f"**Thresholds:** ≤ 1.5% → full marks · ≥ 10.0% → zero  \n"
                f"**Weight:** 30 pts"
            )

        st.divider()
        total = breakdown["total"]
        bar_pct = total / 100
        st.markdown(
            f"**Total: {total} / 100 — {breakdown['overall_label']}**  \n"
            "Score interpretation: **65–100** Stable · **40–64** Moderate · **0–39** Elevated Risk"
        )
        st.progress(bar_pct)


def render_charts(df_ex, df_com, df_fuel) -> None:
    """Render dashboard overview charts."""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("USD/SOS Exchange Rate")
        st.plotly_chart(
            create_exchange_rate_chart(df_ex),
            width='stretch',
            key="dash_ex_chart",
        )

    with col2:
        st.subheader("Commodity Prices — All Categories")
        st.plotly_chart(
            create_commodity_overview_chart(df_com),
            width='stretch',
            key="dash_com_chart",
        )

    st.subheader("Fuel Price Trends")
    st.plotly_chart(
        create_fuel_overview_chart(df_fuel),
        width='stretch',
        key="dash_fuel_chart",
    )


def render_latest_prices_table(df_com, df_fuel) -> None:
    """Render summary tables of the most recent prices."""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Latest Commodity Prices")
        latest_com = (
            df_com.sort_values("date")
            .groupby("commodity", as_index=False)
            .last()
            [["commodity", "price_usd", "unit", "date"]]
            .rename(columns={
                "commodity": "Commodity",
                "price_usd": "Price (USD)",
                "unit": "Unit",
                "date": "Last Updated",
            })
        )
        latest_com["Price (USD)"] = latest_com["Price (USD)"].map("${:.3f}".format)
        latest_com["Last Updated"] = latest_com["Last Updated"].dt.strftime("%b %Y")
        st.dataframe(latest_com, width='stretch', hide_index=True)

    with col2:
        st.subheader("Latest Fuel Prices")
        latest_fuel = (
            df_fuel.sort_values("date")
            .groupby("fuel_type", as_index=False)
            .last()
            [["fuel_type", "price_usd", "unit", "date"]]
            .rename(columns={
                "fuel_type": "Fuel Type",
                "price_usd": "Price (USD/L)",
                "unit": "Unit",
                "date": "Last Updated",
            })
        )
        latest_fuel["Price (USD/L)"] = latest_fuel["Price (USD/L)"].map("${:.3f}".format)
        latest_fuel["Last Updated"] = latest_fuel["Last Updated"].dt.strftime("%b %Y")
        st.dataframe(latest_fuel, width='stretch', hide_index=True)


def main() -> None:
    """Main dashboard entry point."""
    # Initialize database (idempotent — safe to call on every page load)
    initialize_database()

    render_sidebar_info()

    st.title("🇸🇴 Somalia Market Intelligence Platform")
    st.markdown(
        "_Real-time monitoring of exchange rates, commodity prices, and fuel prices across Somalia._"
    )
    st.divider()

    with st.spinner("Loading market data…"):
        df_ex, df_com, df_fuel = load_all_data()

    breakdown = render_kpi_row(df_ex, df_com, df_fuel)
    render_health_breakdown(breakdown)
    st.divider()
    render_charts(df_ex, df_com, df_fuel)
    st.divider()
    render_latest_prices_table(df_com, df_fuel)

    st.divider()
    col_l, col_r = st.columns([3, 1])
    with col_l:
        st.caption(
            f"Data coverage: {df_ex['date'].min().strftime('%b %Y')} — "
            f"{df_ex['date'].max().strftime('%b %Y')} · "
            f"Source: REER Market Survey, Mogadishu"
        )
    with col_r:
        st.caption("Somalia Market Intelligence Platform v1.0")


if __name__ == "__main__":
    main()
