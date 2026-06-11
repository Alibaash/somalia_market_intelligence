"""
Chart creation module for Somalia Market Intelligence Platform.
All charts use Plotly for interactive visualizations.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Consistent color palette
COLORS = {
    "primary": "#1a5276",
    "secondary": "#2e86c1",
    "accent": "#e74c3c",
    "success": "#27ae60",
    "warning": "#f39c12",
    "neutral": "#95a5a6",
    "background": "#f8f9fa",
}

COMMODITY_COLORS = [
    "#1a5276", "#2e86c1", "#27ae60", "#e67e22", "#8e44ad"
]

FUEL_COLORS = {
    "Diesel": "#e74c3c",
    "Petrol": "#e67e22",
}


def _base_layout(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply a consistent base layout to all figures."""
    fig.update_layout(
        title=title,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=20, t=50, b=40),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#ecf0f1", gridwidth=1)
    fig.update_yaxes(showgrid=True, gridcolor="#ecf0f1", gridwidth=1)
    return fig


def create_exchange_rate_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a line chart of USD/SOS exchange rates over time.

    Args:
        df: Exchange rates DataFrame with 'date' and 'usd_sos' columns.

    Returns:
        Plotly Figure object.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["usd_sos"],
            mode="lines+markers",
            name="USD/SOS",
            line=dict(color=COLORS["primary"], width=2.5),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(26, 82, 118, 0.08)",
            hovertemplate="<b>%{x|%b %Y}</b><br>Rate: %{y:.2f} SOS<extra></extra>",
        )
    )
    fig = _base_layout(fig, "USD / Somali Shilling Exchange Rate")
    fig.update_yaxes(title_text="SOS per 1 USD")
    return fig


def create_exchange_rate_monthly_change(df: pd.DataFrame) -> go.Figure:
    """Bar chart showing month-on-month change in USD/SOS rate."""
    df_sorted = df.sort_values("date").copy()
    df_sorted["change"] = df_sorted["usd_sos"].diff()
    df_sorted = df_sorted.dropna()

    colors = [COLORS["accent"] if v > 0 else COLORS["success"] for v in df_sorted["change"]]

    fig = go.Figure(
        go.Bar(
            x=df_sorted["date"],
            y=df_sorted["change"],
            marker_color=colors,
            name="Monthly Change",
            hovertemplate="<b>%{x|%b %Y}</b><br>Change: %{y:+.2f} SOS<extra></extra>",
        )
    )
    fig = _base_layout(fig, "Month-on-Month Exchange Rate Change")
    fig.update_yaxes(title_text="Change (SOS)")
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["neutral"])
    return fig


def create_commodity_overview_chart(df: pd.DataFrame) -> go.Figure:
    """
    Multi-line chart showing all commodity price trends over time.

    Args:
        df: Commodity prices DataFrame.

    Returns:
        Plotly Figure object.
    """
    fig = go.Figure()
    commodities = df["commodity"].unique()

    for i, commodity in enumerate(sorted(commodities)):
        df_c = df[df["commodity"] == commodity].sort_values("date")
        unit = df_c["unit"].iloc[0]
        fig.add_trace(
            go.Scatter(
                x=df_c["date"],
                y=df_c["price_usd"],
                mode="lines+markers",
                name=commodity,
                line=dict(color=COMMODITY_COLORS[i % len(COMMODITY_COLORS)], width=2),
                marker=dict(size=4),
                hovertemplate=f"<b>{commodity}</b><br>%{{x|%b %Y}}<br>Price: $%{{y:.3f}}/{unit}<extra></extra>",
            )
        )

    fig = _base_layout(fig, "Commodity Price Trends")
    fig.update_yaxes(title_text="Price (USD)")
    return fig


def create_commodity_detail_chart(df: pd.DataFrame, commodity: str) -> go.Figure:
    """Line chart for a single commodity with trend band."""
    df_c = df[df["commodity"] == commodity].sort_values("date").copy()
    unit = df_c["unit"].iloc[0] if len(df_c) > 0 else ""

    rolling_mean = df_c["price_usd"].rolling(3, min_periods=1).mean()
    rolling_std = df_c["price_usd"].rolling(3, min_periods=1).std().fillna(0)

    fig = go.Figure()

    # Confidence band
    fig.add_trace(
        go.Scatter(
            x=pd.concat([df_c["date"], df_c["date"][::-1]]),
            y=pd.concat([rolling_mean + rolling_std, (rolling_mean - rolling_std)[::-1]]),
            fill="toself",
            fillcolor="rgba(46, 134, 193, 0.12)",
            line=dict(color="rgba(255,255,255,0)"),
            name="±1 Std Dev",
            showlegend=True,
        )
    )
    # Trend line
    fig.add_trace(
        go.Scatter(
            x=df_c["date"],
            y=rolling_mean,
            mode="lines",
            line=dict(color=COLORS["secondary"], width=1.5, dash="dash"),
            name="3-Month Avg",
        )
    )
    # Actual prices
    fig.add_trace(
        go.Scatter(
            x=df_c["date"],
            y=df_c["price_usd"],
            mode="lines+markers",
            name=commodity,
            line=dict(color=COLORS["primary"], width=2.5),
            marker=dict(size=6),
            hovertemplate=f"<b>%{{x|%b %Y}}</b><br>Price: $%{{y:.3f}}/{unit}<extra></extra>",
        )
    )

    fig = _base_layout(fig, f"{commodity} — Price History")
    fig.update_yaxes(title_text=f"Price (USD/{unit})")
    return fig


def create_fuel_overview_chart(df: pd.DataFrame) -> go.Figure:
    """Dual-line chart for Diesel and Petrol price trends."""
    fig = go.Figure()

    for fuel_type, color in FUEL_COLORS.items():
        df_f = df[df["fuel_type"] == fuel_type].sort_values("date")
        fig.add_trace(
            go.Scatter(
                x=df_f["date"],
                y=df_f["price_usd"],
                mode="lines+markers",
                name=fuel_type,
                line=dict(color=color, width=2.5),
                marker=dict(size=5),
                hovertemplate=f"<b>{fuel_type}</b><br>%{{x|%b %Y}}<br>$%{{y:.3f}}/L<extra></extra>",
            )
        )

    fig = _base_layout(fig, "Fuel Price Trends — Diesel vs Petrol")
    fig.update_yaxes(title_text="Price (USD/liter)")
    return fig


def create_fuel_detail_chart(df: pd.DataFrame, fuel_type: str) -> go.Figure:
    """Bar chart for a single fuel type with trend overlay."""
    df_f = df[df["fuel_type"] == fuel_type].sort_values("date").copy()
    color = FUEL_COLORS.get(fuel_type, COLORS["primary"])

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_f["date"],
            y=df_f["price_usd"],
            name=fuel_type,
            marker_color=color,
            opacity=0.75,
            hovertemplate=f"<b>{fuel_type}</b><br>%{{x|%b %Y}}<br>$%{{y:.3f}}/L<extra></extra>",
        )
    )
    # Rolling average overlay
    rolling = df_f["price_usd"].rolling(3, min_periods=1).mean()
    fig.add_trace(
        go.Scatter(
            x=df_f["date"],
            y=rolling,
            mode="lines",
            name="3-Month Avg",
            line=dict(color=COLORS["primary"], width=2),
        )
    )
    fig = _base_layout(fig, f"{fuel_type} — Monthly Price")
    fig.update_yaxes(title_text="Price (USD/liter)")
    return fig


def create_volatility_chart(volatility_df: pd.DataFrame, label_col: str) -> go.Figure:
    """Horizontal bar chart of price volatility (CV %) ranked highest to lowest."""
    df_sorted = volatility_df.sort_values("volatility_cv", ascending=True)
    bar_colors = [
        COLORS["accent"] if v > 5 else (COLORS["warning"] if v > 2 else COLORS["success"])
        for v in df_sorted["volatility_cv"]
    ]

    fig = go.Figure(
        go.Bar(
            x=df_sorted["volatility_cv"],
            y=df_sorted[label_col],
            orientation="h",
            marker_color=bar_colors,
            text=df_sorted["volatility_cv"].map("{:.2f}%".format),
            textposition="outside",
            hovertemplate="%{y}<br>CV: %{x:.2f}%<extra></extra>",
        )
    )
    fig = _base_layout(fig, "Price Volatility Ranking (Coefficient of Variation)")
    fig.update_xaxes(title_text="Volatility CV (%)")
    fig.update_layout(legend=dict(visible=False))
    return fig


def create_correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """Interactive heatmap of commodity price correlations."""
    fig = go.Figure(
        go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns.tolist(),
            y=corr_matrix.index.tolist(),
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            text=corr_matrix.values.round(2),
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate="%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>",
            colorbar=dict(title="Correlation"),
        )
    )
    fig.update_layout(
        title="Commodity Price Correlation Matrix",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


def create_price_change_bar(stats_df: pd.DataFrame, label_col: str, period_col: str, period_label: str) -> go.Figure:
    """Bar chart of price changes for a given time period."""
    df_sorted = stats_df.sort_values(period_col, ascending=False)
    bar_colors = [COLORS["accent"] if v > 0 else COLORS["success"] for v in df_sorted[period_col]]

    fig = go.Figure(
        go.Bar(
            x=df_sorted[label_col],
            y=df_sorted[period_col],
            marker_color=bar_colors,
            text=df_sorted[period_col].map("{:+.2f}%".format),
            textposition="outside",
            hovertemplate="%{x}<br>Change: %{y:+.2f}%<extra></extra>",
        )
    )
    fig = _base_layout(fig, f"{period_label} Price Change (%)")
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["neutral"])
    fig.update_yaxes(title_text="Change (%)")
    return fig
