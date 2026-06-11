# 🇸🇴 Somalia Market Intelligence & Price Monitoring Platform

A professional market intelligence platform for Somalia that monitors **exchange rates**, **commodity prices**, **fuel prices**, and **economic indicators**. Built with Python and Streamlit — fully open source, zero external services required.

---

## Features

### 🏠 Dashboard
- Live KPI cards: USD/SOS rate, commodity index, fuel average, Market Health Index
- Interactive overview charts for all market categories
- Market Health Score with component breakdown (exchange rate, commodity, fuel stability)
- Latest prices summary tables

### 💱 Exchange Rates
- Historical USD / Somali Shilling (SOS) rate trends (24 months)
- Month-on-month change bar chart
- Rolling volatility and descriptive statistics
- Full downloadable data table

### 🌾 Commodity Prices
Tracks: **Rice**, **Sugar**, **Wheat Flour**, **Cooking Oil**, **Pasta**
- Current price with MoM change
- Individual commodity detail with 3-month moving average
- 1-month and 3-month price change comparisons
- Full price history table

### ⛽ Fuel Prices
Tracks: **Diesel**, **Petrol**
- Monthly price trends tracking global oil market movements
- Side-by-side fuel comparison charts
- Monthly change analysis

### 📊 Analytics
- Highest increasing / decreasing commodity (MoM)
- Price volatility ranking by Coefficient of Variation (CV%)
- Commodity price correlation heatmap
- Cross-market trend analysis table
- Narrative market insights generated automatically

### 📄 Methodology
- Data sources and collection procedures
- Exchange rate, commodity, and fuel price methodologies
- Volatility (CV) and correlation (Pearson) calculation explanations
- Market Health Index formula, weights, and threshold calibration
- Statistical and geographic limitations

---

## Tech Stack

| Component   | Technology          |
|-------------|---------------------|
| Frontend    | Streamlit ≥ 1.28    |
| Data        | Pandas ≥ 2.0, NumPy |
| Charts      | Plotly ≥ 5.15       |
| Database    | SQLite (built-in)   |
| Language    | Python 3.11+        |

No paid APIs. No external services. No environment variables required.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/somalia-market-intelligence.git
cd somalia-market-intelligence
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

> The SQLite database is created automatically on first launch and seeded with
> 24 months of realistic sample data (January 2023 – December 2024).

---

## Project Structure

```
somalia_market_intelligence/
│
├── app.py                    # Entry point — Dashboard page
├── requirements.txt          # Python dependencies
├── README.md
├── LICENSE                   # MIT
│
├── .streamlit/
│   └── config.toml           # Streamlit server & theme config
│
├── assets/                   # Static assets (logos, images)
│
├── database/
│   └── market_data.db        # Auto-created SQLite database (gitignored)
│
├── pages/                    # Streamlit multipage app
│   ├── 1_Exchange_Rates.py
│   ├── 2_Commodity_Prices.py
│   ├── 3_Fuel_Prices.py
│   ├── 4_Analytics.py
│   └── 5_Methodology.py
│
├── utils/                    # Shared utility modules
│   ├── __init__.py
│   ├── database.py           # DB init, table creation, data seeding
│   ├── loaders.py            # DataFrame loaders from SQLite
│   ├── charts.py             # Plotly chart factory functions
│   └── metrics.py            # KPI, health score, statistical calculations
│
└── docs/                     # Additional documentation
```

---

## Deploying to Streamlit Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Click **"New app"** → select your repository.
4. Set the **Main file path** to `app.py`.
5. Click **"Deploy"** — no secrets or environment variables needed.

> If your repository root contains other files (e.g. from a monorepo), set the
> **App directory** to `somalia_market_intelligence/` in the deployment settings.

---

## Data

The platform ships with **24 months** (Jan 2023 – Dec 2024) of realistic sample
data generated programmatically from real Somalia market benchmarks:

| Dataset          | Source                     | Frequency |
|------------------|----------------------------|-----------|
| USD/SOS Rate     | REER Market Survey         | Monthly   |
| Commodity Prices | Mogadishu wholesale market | Monthly   |
| Fuel Prices      | Pump price surveys         | Monthly   |

All data is stored in a local SQLite database (`database/market_data.db`) that
is created and seeded automatically on first run. The database file is excluded
from version control via `.gitignore`.

---

## License

MIT License © 2024 — See [LICENSE](LICENSE) for details.
