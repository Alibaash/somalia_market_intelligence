"""
Analytics Page — Somalia Market Intelligence Platform
Provides volatility rankings, correlation analysis, trend analysis, and market insights.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from utils.database import initialize_database
from utils.loaders import load_commodity_prices, load_exchange_rates, load_fuel_prices
from utils.charts import (
    create_volatility_chart,
    create_correlation_heatmap,
    create_price_change_bar,
)
from utils.metrics import (
    calculate_price_changes,
    calculate_commodity_correlation,
    get_trend_label,
)

st.set_page_config(
    page_title="Analytics — Somalia MIP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=300)
def get_all_data():
    """Load and cache all datasets."""
    initialize_database()
    return load_exchange_rates(), load_commodity_prices(), load_fuel_prices()


def render_market_insights(df_com, df_fuel) -> None:
    """
    Highlight the top-increasing and top-decreasing commodities
    and provide narrative market insights.
    """
    st.subheader("📌 Market Insights")

    com_stats = calculate_price_changes(df_com, "price_usd", "commodity")
    fuel_stats = calculate_price_changes(df_fuel, "price_usd", "fuel_type")

    top_increase = com_stats.loc[com_stats["change_1m_pct"].idxmax()]
    top_decrease = com_stats.loc[com_stats["change_1m_pct"].idxmin()]
    most_volatile = com_stats.loc[com_stats["volatility_cv"].idxmax()]
    least_volatile = com_stats.loc[com_stats["volatility_cv"].idxmin()]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info(
            f"**📈 Highest Increase (MoM)**  \n"
            f"**{top_increase['commodity']}**  \n"
            f"`+{top_increase['change_1m_pct']:.2f}%`"
        )
    with col2:
        st.success(
            f"**📉 Highest Decrease (MoM)**  \n"
            f"**{top_decrease['commodity']}**  \n"
            f"`{top_decrease['change_1m_pct']:.2f}%`"
        )
    with col3:
        st.warning(
            f"**⚠️ Most Volatile**  \n"
            f"**{most_volatile['commodity']}**  \n"
            f"CV: `{most_volatile['volatility_cv']:.2f}%`"
        )
    with col4:
        st.info(
            f"**✅ Most Stable**  \n"
            f"**{least_volatile['commodity']}**  \n"
            f"CV: `{least_volatile['volatility_cv']:.2f}%`"
        )

    st.divider()

    # Narrative insights
    avg_com_change = com_stats["change_1m_pct"].mean()
    avg_fuel_change = fuel_stats["change_1m_pct"].mean()

    narratives = []

    if avg_com_change > 1.5:
        narratives.append(
            f"⚠️ **Food price pressure**: Average commodity prices rose **{avg_com_change:.1f}%** "
            "this month, indicating inflationary pressure on the food basket."
        )
    elif avg_com_change < -1.5:
        narratives.append(
            f"✅ **Commodity prices easing**: Average prices fell **{abs(avg_com_change):.1f}%** "
            "this month, suggesting improved supply or reduced demand."
        )
    else:
        narratives.append(
            f"✅ **Commodity markets stable**: Average price change of **{avg_com_change:.1f}%** "
            "indicates relative stability in food markets."
        )

    if avg_fuel_change > 2.0:
        narratives.append(
            f"⚠️ **Fuel costs rising**: Average fuel prices increased **{avg_fuel_change:.1f}%**, "
            "which may flow through to transportation and logistics costs."
        )
    elif avg_fuel_change < -2.0:
        narratives.append(
            f"✅ **Fuel costs declining**: Average fuel prices dropped **{abs(avg_fuel_change):.1f}%**, "
            "which could reduce transport costs and support supply chains."
        )
    else:
        narratives.append(
            f"✅ **Fuel prices steady**: Monthly change of **{avg_fuel_change:.1f}%** "
            "suggests stable fuel market conditions."
        )

    if most_volatile["volatility_cv"] > 6:
        narratives.append(
            f"📊 **{most_volatile['commodity']} showing elevated volatility** (CV {most_volatile['volatility_cv']:.1f}%): "
            "This commodity has shown the widest price swings over the tracking period, "
            "suggesting supply chain disruptions or seasonal demand shifts."
        )

    for narrative in narratives:
        st.markdown(f"- {narrative}")


def render_volatility_section(df_com, df_fuel) -> None:
    """Render the volatility ranking charts."""
    st.subheader("📊 Price Volatility Rankings")
    st.markdown(
        "The **Coefficient of Variation (CV%)** measures price volatility relative to the average. "
        "Higher CV% means more volatile and less predictable pricing."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Commodity Volatility**")
        com_stats = calculate_price_changes(df_com, "price_usd", "commodity")
        st.plotly_chart(
            create_volatility_chart(com_stats, "commodity"),
            width='stretch',
            key="vol_commodity",
        )

    with col2:
        st.markdown("**Fuel Volatility**")
        fuel_stats = calculate_price_changes(df_fuel, "price_usd", "fuel_type")
        st.plotly_chart(
            create_volatility_chart(fuel_stats, "fuel_type"),
            width='stretch',
            key="vol_fuel",
        )


def render_correlation_section(df_com) -> None:
    """Render the commodity price correlation heatmap."""
    st.subheader("🔗 Commodity Price Correlation Matrix")
    st.markdown(
        "Correlation measures how closely two commodity prices move together. "
        "**+1.0** = perfectly correlated, **0** = no relationship, **-1.0** = inverse relationship."
    )

    corr_matrix = calculate_commodity_correlation(df_com)
    st.plotly_chart(
        create_correlation_heatmap(corr_matrix),
        width='stretch',
        key="corr_heatmap",
    )

    st.markdown("**Interpretation:**")
    strong_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            val = corr_matrix.iloc[i, j]
            c1 = corr_matrix.columns[i]
            c2 = corr_matrix.columns[j]
            if abs(val) >= 0.80:
                direction = "positively" if val > 0 else "negatively"
                strong_pairs.append(f"- **{c1}** and **{c2}** are strongly {direction} correlated (`r = {val:.2f}`)")

    if strong_pairs:
        for p in strong_pairs:
            st.markdown(p)
    else:
        st.markdown("- No strong correlations (|r| ≥ 0.80) detected in this dataset.")


def render_trend_analysis(df_com, df_ex, df_fuel) -> None:
    """Render the trend comparison across all market indicators."""
    st.subheader("📈 Cross-Market Trend Analysis")

    com_stats = calculate_price_changes(df_com, "price_usd", "commodity")
    fuel_stats = calculate_price_changes(df_fuel, "price_usd", "fuel_type")

    all_stats = []

    for _, row in com_stats.iterrows():
        all_stats.append({
            "Indicator": row["commodity"],
            "Category": "Commodity",
            "Latest Price (USD)": f"${row['latest_price']:.3f}",
            "1M Change (%)": row["change_1m_pct"],
            "3M Change (%)": row["change_3m_pct"],
            "YTD Change (%)": row["change_ytd_pct"],
            "Volatility CV (%)": row["volatility_cv"],
            "Trend": get_trend_label(row["change_1m_pct"]),
        })

    for _, row in fuel_stats.iterrows():
        all_stats.append({
            "Indicator": row["fuel_type"],
            "Category": "Fuel",
            "Latest Price (USD)": f"${row['latest_price']:.3f}",
            "1M Change (%)": row["change_1m_pct"],
            "3M Change (%)": row["change_3m_pct"],
            "YTD Change (%)": row["change_ytd_pct"],
            "Volatility CV (%)": row["volatility_cv"],
            "Trend": get_trend_label(row["change_1m_pct"]),
        })

    df_all = pd.DataFrame(all_stats)
    st.dataframe(df_all, width='stretch', hide_index=True)

    # YTD bar chart
    st.subheader("Year-to-Date Price Changes — All Indicators")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Commodities — YTD Change**")
        st.plotly_chart(
            create_price_change_bar(com_stats, "commodity", "change_ytd_pct", "YTD Commodity"),
            width='stretch',
            key="ytd_com_bar",
        )
    with col2:
        st.markdown("**Fuel — YTD Change**")
        st.plotly_chart(
            create_price_change_bar(fuel_stats, "fuel_type", "change_ytd_pct", "YTD Fuel"),
            width='stretch',
            key="ytd_fuel_bar",
        )


def main() -> None:
    st.title("📊 Analytics")
    st.markdown(
        "Advanced market analysis: volatility rankings, price correlations, "
        "cross-market trends, and actionable market insights."
    )
    st.divider()

    df_ex, df_com, df_fuel = get_all_data()

    render_market_insights(df_com, df_fuel)

    tab1, tab2, tab3 = st.tabs([
        "📊 Volatility Rankings",
        "🔗 Correlation Analysis",
        "📈 Trend Analysis",
    ])

    with tab1:
        render_volatility_section(df_com, df_fuel)

    with tab2:
        render_correlation_section(df_com)

    with tab3:
        render_trend_analysis(df_com, df_ex, df_fuel)

    st.divider()
    st.caption(
        f"Analysis period: {df_com['date'].min().strftime('%b %Y')} — "
        f"{df_com['date'].max().strftime('%b %Y')} · "
        "Source: REER Market Survey, Mogadishu"
    )


if __name__ == "__main__":
    main()
