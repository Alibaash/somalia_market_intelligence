"""
Data loader module for Somalia Market Intelligence Platform.
Loads exchange rate, commodity, and fuel data from the SQLite database
into pandas DataFrames ready for display and analysis.
"""

import os
import pandas as pd

from utils.database import get_connection, initialize_database

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _ensure_db() -> None:
    """Ensure database is initialized before loading data."""
    initialize_database()


def load_exchange_rates() -> pd.DataFrame:
    """
    Load exchange rate data from the database.

    Returns:
        DataFrame with columns: date, usd_sos, source
    """
    _ensure_db()
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT date, usd_sos, source FROM exchange_rates ORDER BY date",
            conn,
        )
    finally:
        conn.close()

    df["date"] = pd.to_datetime(df["date"])
    df["usd_sos"] = df["usd_sos"].astype(float)
    _export_csv(df, "exchange_rates.csv")
    return df


def load_commodity_prices() -> pd.DataFrame:
    """
    Load commodity price data from the database.

    Returns:
        DataFrame with columns: date, commodity, price_usd, unit, city
    """
    _ensure_db()
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT date, commodity, price_usd, unit, city FROM commodity_prices ORDER BY date",
            conn,
        )
    finally:
        conn.close()

    df["date"] = pd.to_datetime(df["date"])
    df["price_usd"] = df["price_usd"].astype(float)
    _export_csv(df, "commodity_prices.csv")
    return df


def load_fuel_prices() -> pd.DataFrame:
    """
    Load fuel price data from the database.

    Returns:
        DataFrame with columns: date, fuel_type, price_usd, unit, city
    """
    _ensure_db()
    conn = get_connection()
    try:
        df = pd.read_sql_query(
            "SELECT date, fuel_type, price_usd, unit, city FROM fuel_prices ORDER BY date",
            conn,
        )
    finally:
        conn.close()

    df["date"] = pd.to_datetime(df["date"])
    df["price_usd"] = df["price_usd"].astype(float)
    _export_csv(df, "fuel_prices.csv")
    return df


def _export_csv(df: pd.DataFrame, filename: str) -> None:
    """Export a DataFrame to the data/ directory as CSV (for GitHub reference)."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        df.to_csv(path, index=False)
