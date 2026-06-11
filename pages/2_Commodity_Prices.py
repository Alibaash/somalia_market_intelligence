"""
Commodity Prices Page — Somalia Market Intelligence Platform
Tracks Rice, Sugar, Wheat Flour, Cooking Oil, and Pasta prices in Mogadishu.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from utils.database import initialize_database
from utils.loaders import load_commodity_prices
from utils.charts import (
    create_commodity_overview_chart,
    create_commodity_detail_chart,
    create_price_change_bar,
)
from utils.metrics import calculate_price_changes

st.set_page_config(
    page_title="Commodity Prices — Somalia MIP",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

COMMODITY_ICONS = {
    "Rice": "🌾",
    "Sugar": "🍬",
    "Wheat Flour": "🌾",
    "Cooking Oil": "🫙",
    "Pasta": "🍝",
}


@st.cache_data(ttl=300)
def get_data():
    """Load and cache commodity price data."""
    initialize_database()
    return load_commodity_prices()


def render_summary_metrics(df) -> None:
    """Display latest price metrics for all commodities."""
    stats = calculate_price_changes(df, "price_usd", "commodity")
    commodities = sorted(df["commodity"].unique())
    cols = st.columns(len(commodities))

    for col, commodity in zip(cols, commodities):
        row = stats[stats["commodity"] == commodity].iloc[0]
        icon = COMMODITY_ICONS.get(commodity, "📦")
        unit = df[df["commodity"] == commodity]["unit"].iloc[0]
        with col:
            st.metric(
                label=f"{icon} {commodity}",
                value=f"${row['latest_price']:.3f}/{unit}",
                delta=f"{row['change_1m_pct']:+.2f}% MoM",
                delta_color="inverse",
            )


def render_overview_chart(df) -> None:
    """Render the multi-commodity overview chart."""
    st.subheader("All Commodities — Price Trends")
    st.plotly_chart(
        create_commodity_overview_chart(df),
        width='stretch',
        key="com_overview",
    )


def render_commodity_detail(df) -> None:
    """Render a detailed view for a user-selected commodity."""
    st.subheader("Single Commodity Detail")

    commodities = sorted(df["commodity"].unique())
    selected = st.selectbox(
        "Select a commodity to inspect:",
        commodities,
        key="com_selector",
    )

    df_selected = df[df["commodity"] == selected]
    unit = df_selected["unit"].iloc[0]
    stats = calculate_price_changes(df, "price_usd", "commodity")
    row = stats[stats["commodity"] == selected].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"${row['latest_price']:.3f}/{unit}")
    with col2:
        st.metric("1-Month Change", f"{row['change_1m_pct']:+.2f}%", delta_color="inverse")
    with col3:
        st.metric("3-Month Change", f"{row['change_3m_pct']:+.2f}%", delta_color="inverse")
    with col4:
        st.metric("Volatility (CV)", f"{row['volatility_cv']:.2f}%")

    st.plotly_chart(
        create_commodity_detail_chart(df, selected),
        width='stretch',
        key="com_detail_chart",
    )


def render_price_changes_chart(df) -> None:
    """Render price change comparison charts."""
    stats = calculate_price_changes(df, "price_usd", "commodity")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1-Month Price Changes")
        st.plotly_chart(
            create_price_change_bar(stats, "commodity", "change_1m_pct", "1-Month"),
            width='stretch',
            key="com_1m_bar",
        )
    with col2:
        st.subheader("3-Month Price Changes")
        st.plotly_chart(
            create_price_change_bar(stats, "commodity", "change_3m_pct", "3-Month"),
            width='stretch',
            key="com_3m_bar",
        )


def render_data_table(df) -> None:
    """Render the full commodity price history table."""
    st.subheader("Full Price History")

    commodities = ["All"] + sorted(df["commodity"].unique().tolist())
    filter_com = st.selectbox("Filter by commodity:", commodities, key="com_table_filter")

    df_display = df.copy()
    if filter_com != "All":
        df_display = df_display[df_display["commodity"] == filter_com]

    df_display = df_display.sort_values(["date", "commodity"], ascending=[False, True])
    df_display["date"] = df_display["date"].dt.strftime("%B %Y")
    df_display = df_display.rename(columns={
        "date": "Month",
        "commodity": "Commodity",
        "price_usd": "Price (USD)",
        "unit": "Unit",
        "city": "City",
    })
    df_display["Price (USD)"] = df_display["Price (USD)"].map("${:.3f}".format)
    st.dataframe(df_display[["Month", "Commodity", "Price (USD)", "Unit", "City"]], width='stretch', hide_index=True)


def render_statistics_table(df) -> None:
    """Render a statistics summary table across all commodities."""
    st.subheader("Summary Statistics by Commodity")
    stats = calculate_price_changes(df, "price_usd", "commodity")
    stats_display = stats.rename(columns={
        "commodity": "Commodity",
        "latest_price": "Latest Price (USD)",
        "change_1m_pct": "1M Change (%)",
        "change_3m_pct": "3M Change (%)",
        "change_ytd_pct": "YTD Change (%)",
        "volatility_cv": "Volatility CV (%)",
    })
    stats_display["Latest Price (USD)"] = stats_display["Latest Price (USD)"].map("${:.3f}".format)

    def color_change(val):
        """Style positive/negative change values."""
        try:
            v = float(val)
            color = "color: #e74c3c" if v > 0 else "color: #27ae60"
            return color
        except (ValueError, TypeError):
            return ""

    styled = stats_display.style.map(
        color_change,
        subset=["1M Change (%)", "3M Change (%)", "YTD Change (%)"],
    )
    st.dataframe(styled, width='stretch', hide_index=True)


def main() -> None:
    st.title("🌾 Commodity Prices")
    st.markdown(
        "Monthly price tracking for key food commodities in Mogadishu's wholesale markets. "
        "Prices are reported in **USD per kg** (or liter for Cooking Oil)."
    )
    st.divider()

    df = get_data()

    render_summary_metrics(df)
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview Chart",
        "🔍 Commodity Detail",
        "📊 Price Changes",
        "📋 Data Table",
    ])

    with tab1:
        render_overview_chart(df)
        st.divider()
        render_statistics_table(df)

    with tab2:
        render_commodity_detail(df)

    with tab3:
        render_price_changes_chart(df)

    with tab4:
        render_data_table(df)

    st.divider()
    st.caption(
        f"Coverage: {df['date'].min().strftime('%b %Y')} — {df['date'].max().strftime('%b %Y')} · "
        "Source: REER Market Survey, Mogadishu · Prices in USD"
    )


if __name__ == "__main__":
    main()
