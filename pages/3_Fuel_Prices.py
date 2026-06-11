"""
Fuel Prices Page — Somalia Market Intelligence Platform
Tracks Diesel and Petrol prices in Mogadishu, with trends and monthly changes.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from utils.database import initialize_database
from utils.loaders import load_fuel_prices
from utils.charts import (
    create_fuel_overview_chart,
    create_fuel_detail_chart,
    create_price_change_bar,
)
from utils.metrics import calculate_price_changes, get_trend_label

st.set_page_config(
    page_title="Fuel Prices — Somalia MIP",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

FUEL_ICONS = {"Diesel": "🚛", "Petrol": "🚗"}


@st.cache_data(ttl=300)
def get_data():
    """Load and cache fuel price data."""
    initialize_database()
    return load_fuel_prices()


def render_kpis(df) -> None:
    """Display fuel price KPI metrics."""
    stats = calculate_price_changes(df, "price_usd", "fuel_type")

    cols = st.columns(len(stats) * 2 + 1)
    col_idx = 0

    for _, row in stats.iterrows():
        fuel = row["fuel_type"]
        icon = FUEL_ICONS.get(fuel, "⛽")
        with cols[col_idx]:
            st.metric(
                label=f"{icon} {fuel} (USD/L)",
                value=f"${row['latest_price']:.3f}",
                delta=f"{row['change_1m_pct']:+.2f}% MoM",
                delta_color="inverse",
            )
        col_idx += 1
        with cols[col_idx]:
            st.metric(
                label=f"{fuel} — 3M Change",
                value=f"{row['change_3m_pct']:+.2f}%",
                delta=get_trend_label(row["change_3m_pct"]),
                delta_color="off",
            )
        col_idx += 1

    with cols[col_idx]:
        combined_latest = stats["latest_price"].mean()
        st.metric(
            label="⛽ Blended Avg Price",
            value=f"${combined_latest:.3f}/L",
        )


def render_overview_chart(df) -> None:
    """Render the combined Diesel + Petrol chart."""
    st.subheader("Diesel vs Petrol — Price Comparison")
    st.plotly_chart(
        create_fuel_overview_chart(df),
        width='stretch',
        key="fuel_overview",
    )


def render_individual_charts(df) -> None:
    """Render side-by-side detail charts for each fuel type."""
    fuel_types = sorted(df["fuel_type"].unique())
    cols = st.columns(len(fuel_types))

    for col, fuel_type in zip(cols, fuel_types):
        with col:
            st.subheader(f"{FUEL_ICONS.get(fuel_type, '⛽')} {fuel_type}")
            st.plotly_chart(
                create_fuel_detail_chart(df, fuel_type),
                width='stretch',
                key=f"fuel_detail_{fuel_type}",
            )


def render_monthly_changes_chart(df) -> None:
    """Render bar chart of 1-month and 3-month changes."""
    stats = calculate_price_changes(df, "price_usd", "fuel_type")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1-Month Price Change")
        st.plotly_chart(
            create_price_change_bar(stats, "fuel_type", "change_1m_pct", "1-Month Fuel"),
            width='stretch',
            key="fuel_1m_bar",
        )
    with col2:
        st.subheader("3-Month Price Change")
        st.plotly_chart(
            create_price_change_bar(stats, "fuel_type", "change_3m_pct", "3-Month Fuel"),
            width='stretch',
            key="fuel_3m_bar",
        )


def render_data_table(df) -> None:
    """Render full fuel price history."""
    st.subheader("Historical Fuel Prices")

    fuel_types = ["All"] + sorted(df["fuel_type"].unique().tolist())
    filter_type = st.selectbox("Filter by fuel type:", fuel_types, key="fuel_filter")

    df_display = df.copy()
    if filter_type != "All":
        df_display = df_display[df_display["fuel_type"] == filter_type]

    df_display = df_display.sort_values(["date", "fuel_type"], ascending=[False, True])
    df_display["date"] = df_display["date"].dt.strftime("%B %Y")
    df_display = df_display.rename(columns={
        "date": "Month",
        "fuel_type": "Fuel Type",
        "price_usd": "Price (USD/L)",
        "unit": "Unit",
        "city": "City",
    })
    df_display["Price (USD/L)"] = df_display["Price (USD/L)"].map("${:.3f}".format)
    st.dataframe(
        df_display[["Month", "Fuel Type", "Price (USD/L)", "City"]],
        width='stretch',
        hide_index=True,
    )


def render_statistics_table(df) -> None:
    """Render fuel price statistics summary."""
    st.subheader("Fuel Price Statistics")
    stats = calculate_price_changes(df, "price_usd", "fuel_type")
    stats_display = stats.rename(columns={
        "fuel_type": "Fuel Type",
        "latest_price": "Latest (USD/L)",
        "change_1m_pct": "1M Change (%)",
        "change_3m_pct": "3M Change (%)",
        "change_ytd_pct": "YTD Change (%)",
        "volatility_cv": "Volatility CV (%)",
    })
    stats_display["Latest (USD/L)"] = stats_display["Latest (USD/L)"].map("${:.3f}".format)
    st.dataframe(stats_display, width='stretch', hide_index=True)


def main() -> None:
    st.title("⛽ Fuel Prices")
    st.markdown(
        "Monthly Diesel and Petrol price tracking in Mogadishu. "
        "Prices reported in **USD per liter**. Fuel prices are sensitive to global oil markets and logistics."
    )
    st.divider()

    df = get_data()

    render_kpis(df)
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Price Trends",
        "🔍 Individual Fuel",
        "📊 Monthly Changes",
        "📋 Data Table",
    ])

    with tab1:
        render_overview_chart(df)
        st.divider()
        render_statistics_table(df)

    with tab2:
        render_individual_charts(df)

    with tab3:
        render_monthly_changes_chart(df)

    with tab4:
        render_data_table(df)

    st.divider()
    st.caption(
        f"Coverage: {df['date'].min().strftime('%b %Y')} — {df['date'].max().strftime('%b %Y')} · "
        "Source: REER Market Survey, Mogadishu · Prices in USD/liter"
    )


if __name__ == "__main__":
    main()
