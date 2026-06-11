"""
Exchange Rates Page — Somalia Market Intelligence Platform
Displays historical USD/SOS exchange rate trends, monthly changes, and statistics.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from utils.database import initialize_database
from utils.loaders import load_exchange_rates
from utils.charts import create_exchange_rate_chart, create_exchange_rate_monthly_change
from utils.metrics import get_latest_exchange_rate, calculate_price_changes

st.set_page_config(
    page_title="Exchange Rates — Somalia MIP",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=300)
def get_data():
    """Load and cache exchange rate data."""
    initialize_database()
    return load_exchange_rates()


def render_kpis(df) -> None:
    """Display exchange rate KPI metrics."""
    latest_rate, monthly_change = get_latest_exchange_rate(df)
    df_sorted = df.sort_values("date")

    # Calculate additional stats
    rate_12m_ago = df_sorted["usd_sos"].iloc[-13] if len(df_sorted) >= 13 else df_sorted["usd_sos"].iloc[0]
    annual_change = round(latest_rate - rate_12m_ago, 2)
    annual_change_pct = round((annual_change / rate_12m_ago) * 100, 2)

    ytd_start = df_sorted.iloc[0]["usd_sos"]
    ytd_change_pct = round(((latest_rate - ytd_start) / ytd_start) * 100, 2)

    avg_rate = round(df["usd_sos"].mean(), 2)
    min_rate = round(df["usd_sos"].min(), 2)
    max_rate = round(df["usd_sos"].max(), 2)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Current Rate (USD/SOS)", f"{latest_rate:,.2f}", f"{monthly_change:+.2f} MoM", delta_color="inverse")
    with col2:
        st.metric("Annual Change", f"{annual_change:+.2f} SOS", f"{annual_change_pct:+.2f}% YoY", delta_color="inverse")
    with col3:
        st.metric("24-Month Average", f"{avg_rate:,.2f}")
    with col4:
        st.metric("24-Month Low", f"{min_rate:,.2f}")
    with col5:
        st.metric("24-Month High", f"{max_rate:,.2f}")


def render_charts(df) -> None:
    """Render exchange rate charts."""
    st.subheader("Historical USD/SOS Rate (24 Months)")
    st.plotly_chart(
        create_exchange_rate_chart(df),
        width='stretch',
        key="ex_line_chart",
    )

    st.subheader("Month-on-Month Change")
    st.plotly_chart(
        create_exchange_rate_monthly_change(df),
        width='stretch',
        key="ex_bar_chart",
    )


def render_data_table(df) -> None:
    """Render the full exchange rate data table."""
    st.subheader("Full Historical Data")

    df_display = df.sort_values("date", ascending=False).copy()
    df_display["Monthly Change"] = df_display["usd_sos"].diff(-1).round(2)
    df_display["Monthly Change %"] = (df_display["usd_sos"].pct_change(-1) * 100).round(3)
    df_display["date"] = df_display["date"].dt.strftime("%B %Y")
    df_display = df_display.rename(columns={
        "date": "Month",
        "usd_sos": "USD/SOS Rate",
        "source": "Source",
    })
    df_display = df_display[["Month", "USD/SOS Rate", "Monthly Change", "Monthly Change %", "Source"]]

    st.dataframe(df_display, width='stretch', hide_index=True)


def render_statistics(df) -> None:
    """Display descriptive statistics for the exchange rate series."""
    st.subheader("Statistical Summary")
    col1, col2 = st.columns(2)

    with col1:
        stats = df["usd_sos"].describe().round(4).rename({
            "count": "Observations",
            "mean": "Mean",
            "std": "Std Dev",
            "min": "Minimum",
            "25%": "Q1 (25th pct)",
            "50%": "Median",
            "75%": "Q3 (75th pct)",
            "max": "Maximum",
        })
        st.dataframe(
            stats.reset_index().rename(columns={"index": "Statistic", "usd_sos": "Value"}),
            width='stretch',
            hide_index=True,
        )

    with col2:
        # Rolling 3-month volatility
        df_vol = df.sort_values("date").copy()
        df_vol["Rolling Std (3M)"] = df_vol["usd_sos"].rolling(3).std().round(4)
        df_vol["date"] = df_vol["date"].dt.strftime("%b %Y")
        df_vol = df_vol[["date", "usd_sos", "Rolling Std (3M)"]].dropna()
        df_vol = df_vol.rename(columns={"date": "Month", "usd_sos": "USD/SOS Rate"})
        st.markdown("**Rolling 3-Month Volatility**")
        st.dataframe(df_vol.tail(12), width='stretch', hide_index=True)


def main() -> None:
    st.title("💱 Exchange Rates")
    st.markdown(
        "Historical USD to Somali Shilling (SOS) exchange rates tracked via "
        "REER (Real Effective Exchange Rate) market surveys in Mogadishu."
    )
    st.divider()

    df = get_data()

    render_kpis(df)
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📈 Charts", "📋 Data Table", "📐 Statistics"])

    with tab1:
        render_charts(df)
    with tab2:
        render_data_table(df)
    with tab3:
        render_statistics(df)

    st.divider()
    st.caption(
        f"Coverage: {df['date'].min().strftime('%b %Y')} — {df['date'].max().strftime('%b %Y')} · "
        "Source: REER Market Survey, Mogadishu"
    )


if __name__ == "__main__":
    main()
