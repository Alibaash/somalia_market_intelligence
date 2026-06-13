# 🇸🇴 Somalia Market Intelligence & Price Monitoring Platform

A web-based market intelligence platform designed to monitor and analyze key economic indicators in Somalia, including exchange rates, commodity prices, fuel prices, and overall market conditions.

Built with Python, Streamlit, Pandas, Plotly, and SQLite, the platform provides interactive dashboards and market analytics in a lightweight, fully open-source solution.

## 🌐 Live Application

**View the live dashboard:**

https://somalia-open-data-app-5mejzs3dqrpeekdirxmb5w.streamlit.app/

---

## 📌 Project Overview

Reliable market information is essential for economic planning, business decision-making, humanitarian response, and research. This platform brings together multiple market indicators into a single dashboard, enabling users to monitor trends, compare prices, and evaluate market performance over time.

The system focuses on three major market components:

* USD/SOS Exchange Rates
* Commodity Prices
* Fuel Prices

It also provides analytical tools such as volatility measurements, correlation analysis, trend monitoring, and a Market Health Index.

---

## ✨ Features

### 🏠 Dashboard

* Market overview dashboard
* Key performance indicators (KPIs)
* Market Health Index
* Exchange rate summary
* Commodity market summary
* Fuel market summary
* Interactive charts and visualizations

### 💱 Exchange Rate Monitoring

* Historical USD/SOS exchange rate trends
* Monthly exchange rate analysis
* Volatility tracking
* Statistical summaries
* Interactive visualizations

### 🌾 Commodity Price Monitoring

Tracks:

* Rice
* Sugar
* Wheat Flour
* Cooking Oil
* Pasta

Features include:

* Historical price trends
* Monthly price comparisons
* Moving average analysis
* Commodity performance tracking

### ⛽ Fuel Price Monitoring

Tracks:

* Diesel
* Petrol

Features include:

* Historical fuel price trends
* Comparative fuel analysis
* Monthly price changes
* Fuel market monitoring

### 📊 Market Analytics

* Commodity volatility ranking
* Correlation analysis
* Cross-market trend evaluation
* Market insights generation
* Market Health Score calculations

### 📄 Methodology

Comprehensive documentation covering:

* Data collection procedures
* Exchange rate methodology
* Commodity price methodology
* Fuel price methodology
* Statistical calculations
* Market Health Index framework
* Study limitations

---

## 📈 Data Coverage

The platform currently contains sample market data covering:

| Dataset          | Coverage            |
| ---------------- | ------------------- |
| Exchange Rates   | Jan 2023 – Dec 2024 |
| Commodity Prices | Jan 2023 – Dec 2024 |
| Fuel Prices      | Jan 2023 – Dec 2024 |

The SQLite database is automatically generated and populated during first launch.

---

## 🛠 Technology Stack

| Component            | Technology   |
| -------------------- | ------------ |
| Programming Language | Python 3.11+ |
| Framework            | Streamlit    |
| Data Analysis        | Pandas       |
| Numerical Computing  | NumPy        |
| Data Visualization   | Plotly       |
| Database             | SQLite       |

### Dependencies

* Streamlit
* Pandas
* NumPy
* Plotly

No paid APIs, external services, or environment variables are required.

---

## 📂 Project Structure

```text
somalia_market_intelligence/
│
├── app.py
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│
├── data/
│
├── database/
│
├── docs/
│
├── pages/
│   ├── 1_Exchange_Rates.py
│   ├── 2_Commodity_Prices.py
│   ├── 3_Fuel_Prices.py
│   ├── 4_Analytics.py
│   └── 5_Methodology.py
│
└── utils/
    ├── __init__.py
    ├── charts.py
    ├── database.py
    ├── loaders.py
    └── metrics.py
```

---

## 🚀 Local Installation

### Clone the Repository

```bash
git clone https://github.com/Alibaash/somalia_market_intelligence.git
cd somalia_market_intelligence
```

### Create a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

## ☁️ Deployment

This application is fully compatible with Streamlit Community Cloud.

Deployment requirements:

1. Push the repository to GitHub.
2. Create a new Streamlit Cloud application.
3. Connect your GitHub repository.
4. Set the main file path to:

```text
app.py
```

5. Deploy.

No API keys, secrets, or external services are required.

---

## 🎯 Intended Users

This platform can support:

* Researchers
* Students
* Market Analysts
* NGOs and Humanitarian Organizations
* Policymakers
* Development Practitioners
* Business Owners
* Economic Monitoring Teams

---

## 🔮 Future Enhancements

Planned improvements include:

* Additional commodity categories
* Regional market comparisons
* CSV and Excel exports
* Forecasting and predictive analytics
* Real-time data integration
* Multi-language support (English and Somali)
* Mobile dashboard optimization

---


## 📜 License

This project is licensed under the MIT License.

See the LICENSE file for details.

---

## 👨‍💻 Author

**Ali Baash**

GitHub Repository:
https://github.com/Alibaash/somalia_market_intelligence

Live Application:
https://somalia-open-data-app-5mejzs3dqrpeekdirxmb5w.streamlit.app/

---

### Supporting Open Data and Market Transparency in Somalia 🇸🇴
