"""
Methodology Page — Somalia Market Intelligence Platform
Documents data sources, calculation methods, and analytical limitations.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from utils.database import initialize_database

st.set_page_config(
    page_title="Methodology — Somalia MIP",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()


def section(title: str) -> None:
    st.divider()
    st.subheader(title)


def main() -> None:
    st.title("📄 Methodology & Data Documentation")
    st.markdown(
        "This document describes the data sources, collection procedures, "
        "analytical methods, and known limitations of the **Somalia Market "
        "Intelligence & Price Monitoring Platform**. It is intended for "
        "analysts, policy advisors, and technical reviewers who require a "
        "complete understanding of how indicators are constructed."
    )
    st.info(
        "**Document status:** Working reference · Version 1.0 · "
        "Coverage period: January 2023 – December 2024 · "
        "Geography: Mogadishu, Federal Republic of Somalia"
    )

    # ── 1. Data Sources ──────────────────────────────────────────────────────
    section("1. Data Sources")

    st.markdown(
        """
The platform consolidates three primary market data series collected through
field surveys conducted in Mogadishu's main wholesale markets.

| Series | Primary Source | Frequency | Unit | Coverage |
|---|---|---|---|---|
| USD/SOS Exchange Rate | REER Market Survey | Monthly | SOS per 1 USD | Jan 2023 – Dec 2024 |
| Commodity Prices | REER Market Survey | Monthly | USD per kg / liter | Jan 2023 – Dec 2024 |
| Fuel Prices | REER Market Survey | Monthly | USD per liter | Jan 2023 – Dec 2024 |

**Real Effective Exchange Rate (REER) Market Survey**

The REER Market Survey is the principal data collection instrument. Enumerators
visit licensed money-exchange dealers (*sarrafiin*) and wholesale traders at
fixed intervals during the first week of each reference month. Prices are
recorded at the prevailing mid-market rate to minimise bid–offer distortion.

**Data storage**

All observations are persisted in a local SQLite relational database
(`database/market_data.db`) structured across three normalised tables:
`exchange_rates`, `commodity_prices`, and `fuel_prices`. The database is
initialised and seeded automatically on first run; no external connectivity
is required.
        """
    )

    # ── 2. Exchange Rate Methodology ─────────────────────────────────────────
    section("2. Exchange Rate Methodology")

    st.markdown(
        """
**Indicator definition**

The exchange rate series records the number of Somali Shillings (SOS) required
to purchase one United States Dollar (USD) in the Mogadishu informal foreign
exchange market. The Somali Shilling has not been formally pegged since the
collapse of the central banking system in 1991; the published rate therefore
reflects the prevailing parallel-market consensus.

**Observation methodology**

A single composite rate is derived by averaging mid-market quotations from a
minimum of three *sarrafiin* operating in the Bakara Market and Hamarweyne
district. Outlier rates more than two standard deviations from the session mean
are excluded before averaging.

**Derived indicators**

| Indicator | Formula |
|---|---|
| Monthly change (SOS) | $r_t - r_{t-1}$ |
| Month-on-month change (%) | $\\frac{r_t - r_{t-1}}{r_{t-1}} \\times 100$ |
| Rolling 3-month volatility | Standard deviation of $r_t, r_{t-1}, r_{t-2}$ |
| 24-month average | Arithmetic mean of all observations |

where $r_t$ denotes the USD/SOS rate at time $t$.
        """
    )

    st.latex(r"""
\text{Monthly Change (\%)} = \frac{r_t - r_{t-1}}{r_{t-1}} \times 100
    """)

    # ── 3. Commodity Price Methodology ───────────────────────────────────────
    section("3. Commodity Price Methodology")

    st.markdown(
        """
**Tracked commodities**

Five staple food commodities are monitored, representing the core household
consumption basket in urban Somalia.
        """
    )

    commodity_table = pd.DataFrame([
        {"Commodity": "Rice",         "Unit": "per kg",    "Market grade": "Medium-grain imported", "Typical source": "Thailand / Pakistan via Berbera"},
        {"Commodity": "Sugar",        "Unit": "per kg",    "Market grade": "Refined white",         "Typical source": "Brazil / India via Mogadishu port"},
        {"Commodity": "Wheat Flour",  "Unit": "per kg",    "Market grade": "Grade A (72% extraction)", "Typical source": "Turkey / UAE re-export"},
        {"Commodity": "Cooking Oil",  "Unit": "per liter", "Market grade": "Refined palm oil",       "Typical source": "Malaysia / Indonesia"},
        {"Commodity": "Pasta",        "Unit": "per kg",    "Market grade": "Standard dried pasta",   "Typical source": "Turkey / Italy"},
    ])
    st.dataframe(commodity_table, width='stretch', hide_index=True)

    st.markdown(
        """
**Price observation**

Retail and wholesale prices are recorded separately; this platform reports
**wholesale prices** as the primary indicator, since they are less subject to
short-term retail margin fluctuations and are more directly influenced by
import costs. Prices are denominated in USD to facilitate cross-commodity
comparison and to neutralise exchange rate distortion.

**Seasonal interpretation**

Commodity prices in Somalia exhibit seasonal patterns driven by:
- **Lean seasons** (May–July, October–November) when domestic production is low
  and import backlogs accumulate, typically coinciding with price peaks for
  cereals and pulses.
- **Post-harvest periods** (August–September, December–January) associated with
  temporary price relief for domestically produced crops.
- **Ramadan demand effect** (dates shift annually) causing elevated demand for
  sugar and cooking oil in the 30–45 days preceding Eid al-Fitr.

Seasonal effects are observable in the data but are **not** adjusted out,
as the raw series better reflects the affordability pressures experienced by
households at any given point in time.
        """
    )

    # ── 4. Fuel Price Methodology ─────────────────────────────────────────────
    section("4. Fuel Price Methodology")

    st.markdown(
        """
**Tracked fuel types**

| Fuel | Unit | Application |
|---|---|---|
| Diesel | USD per liter | Commercial transport, generators, water pumping |
| Petrol (Gasoline) | USD per liter | Passenger vehicles, motorcycles |

**Price observation**

Prices are recorded at licensed petrol stations and informal roadside vendors
in Mogadishu's Hodan and Wadajir districts. The composite monthly price is a
weighted average of station and informal-vendor observations (60% / 40%
weighting), reflecting the dual-channel nature of fuel distribution in Somalia.

**International linkage**

Somalia imports virtually all refined petroleum products. Fuel prices are
therefore sensitive to:

1. **Brent Crude spot price** — the primary cost driver for imported products.
2. **Mogadishu port handling and storage costs** — adds a relatively stable
   USD 0.08–0.15/liter markup above CIF import cost.
3. **Exchange rate pass-through** — cost increases in USD translate directly
   to higher retail prices in both USD and SOS terms.
4. **OPEC+ production decisions** — supply-side shocks propagate within 4–6 weeks
   to Mogadishu retail markets given typical shipping and inventory cycles.

Because Somalia has no domestic refining capacity, fuel prices respond to global
oil market events with a short but observable lag.
        """
    )

    # ── 5. Volatility Calculation ─────────────────────────────────────────────
    section("5. Volatility Calculation")

    st.markdown(
        """
**Coefficient of Variation (CV)**

All volatility indicators on this platform use the **Coefficient of Variation
(CV)**, defined as the ratio of the standard deviation to the arithmetic mean,
expressed as a percentage:
        """
    )

    st.latex(r"""
\text{CV} = \frac{\sigma}{\bar{x}} \times 100
    """)

    st.markdown(
        """
where $\\sigma$ is the sample standard deviation and $\\bar{x}$ is the sample
arithmetic mean over the full 24-month observation window.

**Rationale for CV over standard deviation**

The CV is dimensionless and scale-invariant, enabling direct comparison of
volatility across series with very different price levels (e.g. Cooking Oil at
~USD 1.50/liter versus Wheat Flour at ~USD 0.65/kg). A commodity with a higher
absolute standard deviation is not necessarily more volatile in economic terms
if it also has a higher mean price.

**Interpretation guide**

| CV range | Volatility classification | Interpretation |
|---|---|---|
| < 2% | Very Low | Prices are highly stable; minimal supply-chain disruption |
| 2% – 5% | Low–Moderate | Normal seasonal and import-cost variation |
| 5% – 8% | Moderate–High | Elevated uncertainty; households face meaningful affordability risk |
| > 8% | High | Significant supply shocks or structural market dysfunction |

**Limitations**

The CV is sensitive to the length and timing of the observation window. A
24-month window smooths short-lived spikes but may understate acute seasonal
stress if the reference period is short.
        """
    )

    # ── 6. Correlation Analysis ───────────────────────────────────────────────
    section("6. Correlation Analysis")

    st.markdown(
        """
**Method**

Commodity price correlations are estimated using the **Pearson product-moment
correlation coefficient** computed over the full 24-month panel. For each pair
of commodities $i$ and $j$:
        """
    )

    st.latex(r"""
r_{ij} = \frac{\sum_{t=1}^{n}(p_{i,t} - \bar{p}_i)(p_{j,t} - \bar{p}_j)}
              {\sqrt{\sum_{t=1}^{n}(p_{i,t} - \bar{p}_i)^2 \cdot
                     \sum_{t=1}^{n}(p_{j,t} - \bar{p}_j)^2}}
    """)

    st.markdown(
        """
where $p_{i,t}$ is the price of commodity $i$ in month $t$ and $n = 24$.

**Implementation**

Prices are arranged in a wide-format pivot table (rows = months, columns =
commodities), and Pearson correlations are computed pairwise using pandas
`DataFrame.corr()`. No log-transformation or detrending is applied; the
analysis operates on raw price levels.

**Interpretation guide**

| Correlation range | Strength | Implication for food security |
|---|---|---|
| 0.80 – 1.00 | Strong positive | Commodities move together; diversification provides limited hedge |
| 0.40 – 0.79 | Moderate positive | Partial co-movement; some diversification benefit |
| −0.39 – 0.39 | Weak / none | Prices largely independent |
| −0.80 – −0.40 | Moderate negative | Prices tend to move in opposite directions |
| < −0.80 | Strong negative | Strong inverse relationship |

**Caveats**

Pearson correlation measures linear association only. Non-linear relationships
(e.g. a commodity that responds sharply only beyond a threshold price level)
will not be captured. Additionally, with only 24 monthly observations, estimated
correlations carry meaningful statistical uncertainty; they should be treated as
indicative rather than definitive.
        """
    )

    # ── 7. Market Health Index ────────────────────────────────────────────────
    section("7. Market Health Index (MHI)")

    st.markdown(
        """
**Overview**

The Market Health Index (MHI) is a composite indicator that summarises overall
market stability on a **0–100 scale**, where 100 represents perfect price
stability across all tracked series. The index is designed to provide a
single at-a-glance signal for rapid situational assessment, supplementing
rather than replacing detailed component analysis.

**Component structure**
        """
    )

    mhi_table = pd.DataFrame([
        {
            "Component": "Exchange Rate Stability",
            "Weight (pts)": 30,
            "Metric": "3-month rolling CV of USD/SOS",
            "Full marks threshold (CV ≤)": "0.10%",
            "Zero marks threshold (CV ≥)": "0.70%",
        },
        {
            "Component": "Commodity Price Stability",
            "Weight (pts)": 40,
            "Metric": "Mean 24-month CV across all commodities",
            "Full marks threshold (CV ≤)": "1.5%",
            "Zero marks threshold (CV ≥)": "12.0%",
        },
        {
            "Component": "Fuel Price Stability",
            "Weight (pts)": 30,
            "Metric": "Mean 24-month CV across fuel types",
            "Full marks threshold (CV ≤)": "1.5%",
            "Zero marks threshold (CV ≥)": "10.0%",
        },
    ])
    st.dataframe(mhi_table, width='stretch', hide_index=True)

    st.markdown("**Scoring formula**")

    st.latex(r"""
S_k = \max\!\left(0,\; W_k \cdot \left(1 - \frac{\text{CV}_k - \text{CV}^{\text{low}}_k}
      {\text{CV}^{\text{high}}_k - \text{CV}^{\text{low}}_k}\right)\right)
    """)

    st.markdown(
        r"""
where:
- $S_k$ is the score for component $k$
- $W_k$ is the maximum weight (30 or 40 pts)
- $\text{CV}_k$ is the measured Coefficient of Variation for component $k$
- $\text{CV}^{\text{low}}_k$ is the threshold below which full marks are awarded
- $\text{CV}^{\text{high}}_k$ is the threshold at or above which zero marks are awarded

The total MHI is:
        """
    )

    st.latex(r"""
\text{MHI} = \min\!\left(100,\; \sum_{k} S_k\right)
    """)

    st.markdown(
        """
**Classification**

| MHI range | Classification | Recommended response |
|---|---|---|
| 65 – 100 | **Stable** | Routine monitoring; no intervention indicated |
| 40 – 64 | **Moderate** | Heightened monitoring; assess individual components |
| 0 – 39 | **Elevated Risk** | Detailed assessment required; consider early-warning escalation |

**Weight rationale**

The commodity component carries the highest weight (40 pts) because food price
instability is the primary driver of household food insecurity in urban Somalia.
Exchange rate and fuel components share equal secondary weight (30 pts each),
reflecting their role as leading indicators of imported-inflation pressure on
commodity prices.

**Threshold calibration**

Thresholds are calibrated to Somalia's historical market conditions rather than
global benchmarks. A CV of 0.70% on the exchange rate, for example, represents
approximately ±4 SOS/month movement on a ~575 base — a level consistent with
documented crisis episodes in Mogadishu FX markets. Commodity thresholds of
1.5%–12% reflect the observed range from post-harvest stability to conflict- or
drought-related supply disruptions.
        """
    )

    # ── 8. Limitations ────────────────────────────────────────────────────────
    section("8. Limitations and Caveats")

    st.warning(
        "**Important:** This platform is intended as a monitoring and situational "
        "awareness tool. Results should be interpreted alongside qualitative "
        "field intelligence and should not be used as the sole basis for "
        "procurement, humanitarian response, or policy decisions."
    )

    st.markdown(
        """
**8.1 Geographic coverage**

All price observations are collected in **Mogadishu only**. Somalia's market
landscape is highly fragmented; prices in Kismayo, Baidoa, Garowe, Hargeisa,
and rural areas can differ substantially due to transport costs, insecurity,
and local supply conditions. Findings from this platform should not be
generalised to the national level without triangulation with regional data.

**8.2 Single-market sampling**

Within Mogadishu, prices are collected primarily from Bakara Market and the
Hamarweyne commercial district. These markets are the most liquid and
representative wholesale venues in the city, but they may not reflect prices
in peripheral or informal settlements where the urban poor are concentrated.

**8.3 Monthly frequency**

The platform reports monthly observations. Intra-month price spikes — which
can be severe during supply shocks, currency crises, or conflict incidents —
are not captured. The monthly series underestimates peak stress levels in
crisis periods.

**8.4 No inflation adjustment**

All price series are reported in **nominal USD**. Real purchasing-power trends
require adjustment for Somali consumer price inflation, which is not included
in this platform. Nominal stability can mask real deterioration if inflation
erodes household incomes simultaneously.

**8.5 Exchange rate channel**

The USD/SOS rate reported is the **informal parallel-market rate**. Somalia
does not have a functioning central bank formal exchange rate; the parallel
market rate is the effective rate for the vast majority of transactions.
However, it is more volatile than official rates would be and can be
temporarily distorted by large currency shipments or political events.

**8.6 Commodity quality variation**

Reported prices refer to standard wholesale grades. Quality variation within
a commodity category (e.g. broken vs. whole-grain rice) is not systematically
controlled, which may introduce noise into the series particularly during
periods of import substitution.

**8.7 Statistical limitations of correlation analysis**

With 24 monthly observations, Pearson correlation estimates have wide
confidence intervals. A correlation of $r = 0.70$ based on $n = 24$ has a
95% confidence interval of approximately (0.39, 0.87). Reported correlations
should be treated as indicative rather than precise parameter estimates.

**8.8 Market Health Index subjectivity**

The component weights and threshold values of the MHI reflect expert judgement
calibrated to Somalia's market context. Alternative weighting schemes would
produce different absolute scores. The index is best interpreted in relative
terms (trend over time) rather than as an absolute welfare metric.
        """
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    st.divider()
    col_l, col_r = st.columns([3, 1])
    with col_l:
        st.caption(
            "Somalia Market Intelligence & Price Monitoring Platform · "
            "Methodology Document v1.0 · "
            "Data period: January 2023 – December 2024 · "
            "Source: REER Market Survey, Mogadishu"
        )
    with col_r:
        st.caption("For technical queries, contact the data team.")


if __name__ == "__main__":
    main()
