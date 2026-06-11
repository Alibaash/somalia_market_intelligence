"""
Database utility module for Somalia Market Intelligence Platform.
Handles SQLite initialization, table creation, and sample data seeding.
"""

import sqlite3
import os
import random
from datetime import date
from typing import List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "market_data.db")


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Create normalized database tables if they do not exist."""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            usd_sos     REAL    NOT NULL,
            source      TEXT    DEFAULT 'REER Market Survey',
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commodity_prices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            commodity   TEXT    NOT NULL,
            price_usd   REAL    NOT NULL,
            unit        TEXT    NOT NULL,
            city        TEXT    DEFAULT 'Mogadishu',
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fuel_prices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            fuel_type   TEXT    NOT NULL,
            price_usd   REAL    NOT NULL,
            unit        TEXT    DEFAULT 'liter',
            city        TEXT    DEFAULT 'Mogadishu',
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ex_date  ON exchange_rates(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_com_date ON commodity_prices(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fuel_date ON fuel_prices(date)")

    conn.commit()


def _month_date(start_year: int, start_month: int, offset: int) -> date:
    """Return a date object for the first day of a month offset from start."""
    total = start_month - 1 + offset
    return date(start_year + total // 12, total % 12 + 1, 1)


def generate_exchange_rate_data() -> List[Tuple]:
    """
    Generate 24 months of realistic USD/SOS exchange rate observations (Jan 2023 – Dec 2024).

    Narrative:
    - Q1 2023: mild appreciation driven by hawala/remittance inflows.
    - Q2 2023: sharp depreciation episode (import-cost pressure, FX liquidity crunch).
    - Q3 2023: partial stabilisation as aid flows increase.
    - Q4 2023: gradual resumed depreciation.
    - Q1-Q2 2024: appreciation driven by donor budget support and diaspora remittances.
    - Q3-Q4 2024: levelling off with moderate volatility.

    Noise: ±0.8 SOS (realistic mid-market bid–ask spread effect).
    """
    random.seed(42)

    # Monthly anchor rates — captures the regime changes described above
    anchors = [
        569.8,  # Jan 2023 — appreciation episode begins
        568.4,  # Feb 2023
        567.9,  # Mar 2023
        570.6,  # Apr 2023 — depreciation starts
        574.2,  # May 2023
        578.8,  # Jun 2023 — peak depreciation
        576.3,  # Jul 2023 — partial recovery
        574.5,  # Aug 2023
        575.1,  # Sep 2023
        576.4,  # Oct 2023
        578.0,  # Nov 2023
        577.3,  # Dec 2023
        574.6,  # Jan 2024 — remittance surge
        571.9,  # Feb 2024 — appreciation
        572.5,  # Mar 2024
        573.3,  # Apr 2024
        574.1,  # May 2024
        573.7,  # Jun 2024
        575.0,  # Jul 2024
        576.2,  # Aug 2024
        575.6,  # Sep 2024
        575.2,  # Oct 2024
        576.1,  # Nov 2024
        577.4,  # Dec 2024
    ]

    data = []
    for i, anchor in enumerate(anchors):
        noise = random.uniform(-0.8, 0.8)
        rate = round(anchor + noise, 2)
        d = _month_date(2023, 1, i)
        data.append((d.strftime("%Y-%m-%d"), rate, "REER Market Survey"))
    return data


def generate_commodity_price_data() -> List[Tuple]:
    """
    Generate 24 months of realistic commodity price data for Somalia (Jan 2023 – Dec 2024).
    Each commodity has an independent seasonal profile, trend, and noise level.

    Narratives:
    - Rice: lean-season peak Jul–Sep, post-harvest low Oct–Jan; mild upward trend.
    - Sugar: Ramadan demand spike (Feb–Mar), late-2023 global shortage, then easing.
    - Wheat Flour: elevated H1 2023 (Ukraine/Black-Sea disruption), steady easing H2 2023,
                   gradual recovery H2 2024.
    - Cooking Oil: palm oil market peak H1 2023, sharp correction H2 2023, recovery 2024.
    - Pasta: smoothly wheat-linked, less volatile, slow upward drift.
    """
    random.seed(42)

    # Monthly price anchors per commodity — 24 values
    commodity_anchors = {
        "Rice": [
            0.89, 0.87, 0.86, 0.87, 0.91, 0.96,
            1.04, 1.07, 1.05, 0.97, 0.92, 0.88,
            0.86, 0.85, 0.87, 0.90, 0.94, 0.99,
            1.06, 1.09, 1.07, 0.99, 0.94, 0.91,
        ],
        "Sugar": [
            0.71, 0.75, 0.79, 0.76, 0.71, 0.69,
            0.72, 0.76, 0.81, 0.84, 0.83, 0.80,
            0.77, 0.79, 0.83, 0.80, 0.75, 0.73,
            0.74, 0.72, 0.70, 0.71, 0.73, 0.75,
        ],
        "Wheat Flour": [
            0.66, 0.68, 0.71, 0.73, 0.72, 0.70,
            0.68, 0.65, 0.63, 0.62, 0.64, 0.65,
            0.64, 0.63, 0.64, 0.65, 0.66, 0.65,
            0.64, 0.63, 0.62, 0.63, 0.64, 0.65,
        ],
        "Cooking Oil": [
            1.56, 1.60, 1.63, 1.59, 1.54, 1.49,
            1.43, 1.39, 1.35, 1.33, 1.36, 1.39,
            1.41, 1.44, 1.46, 1.50, 1.53, 1.55,
            1.57, 1.53, 1.50, 1.52, 1.54, 1.56,
        ],
        "Pasta": [
            0.93, 0.95, 0.97, 0.96, 0.95, 0.93,
            0.91, 0.90, 0.89, 0.88, 0.89, 0.90,
            0.91, 0.92, 0.93, 0.94, 0.95, 0.94,
            0.93, 0.92, 0.91, 0.92, 0.93, 0.94,
        ],
    }

    # Per-commodity noise amplitude (±)
    commodity_noise = {
        "Rice": 0.016,
        "Sugar": 0.013,
        "Wheat Flour": 0.011,
        "Cooking Oil": 0.022,
        "Pasta": 0.008,
    }

    commodity_units = {
        "Rice": "kg",
        "Sugar": "kg",
        "Wheat Flour": "kg",
        "Cooking Oil": "liter",
        "Pasta": "kg",
    }

    data = []
    for i in range(24):
        d = _month_date(2023, 1, i)
        for commodity, anchors in commodity_anchors.items():
            noise = random.uniform(-commodity_noise[commodity], commodity_noise[commodity])
            price = round(max(anchors[i] + noise, 0.40), 3)
            data.append((d.strftime("%Y-%m-%d"), commodity, price, commodity_units[commodity], "Mogadishu"))
    return data


def generate_fuel_price_data() -> List[Tuple]:
    """
    Generate 24 months of realistic fuel price data for Somalia (Jan 2023 – Dec 2024).
    Tracks Brent crude with a local distribution/logistics markup.

    Narratives:
    - Diesel: starts elevated (~$0.98), OPEC+ production-cut spike Jun 2023 ($1.08),
              sharp correction Jul–Oct 2023, recovery/plateau Feb–Apr 2024,
              easing through mid-2024, mild uptick Nov–Dec 2024.
    - Petrol: closely tracks Diesel with a ~$0.06 premium; peaks and troughs are
              offset by 1–2 months to reflect different import scheduling.

    Noise: ±0.022 USD/L (spot-market day-to-day spread compressed to monthly obs).
    """
    random.seed(42)

    diesel_anchors = [
        0.98, 0.95, 0.92, 0.93, 0.97, 1.06,
        1.09, 1.04, 0.98, 0.94, 0.91, 0.93,
        0.95, 0.98, 1.01, 0.99, 0.97, 0.95,
        0.93, 0.94, 0.96, 0.98, 0.97, 0.96,
    ]

    petrol_anchors = [
        1.04, 1.01, 0.98, 0.99, 1.03, 1.10,
        1.15, 1.11, 1.05, 1.00, 0.97, 0.99,
        1.01, 1.04, 1.07, 1.05, 1.03, 1.01,
        0.99, 1.00, 1.02, 1.04, 1.03, 1.02,
    ]

    fuel_data = {
        "Diesel": diesel_anchors,
        "Petrol": petrol_anchors,
    }

    noise_amp = 0.022

    data = []
    for i in range(24):
        d = _month_date(2023, 1, i)
        for fuel_type, anchors in fuel_data.items():
            noise = random.uniform(-noise_amp, noise_amp)
            price = round(max(anchors[i] + noise, 0.60), 3)
            data.append((d.strftime("%Y-%m-%d"), fuel_type, price, "liter", "Mogadishu"))
    return data


def seed_database(conn: sqlite3.Connection) -> None:
    """Populate the database with sample data if tables are empty."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM exchange_rates")
    if cursor.fetchone()[0] > 0:
        return  # Already seeded — skip

    cursor.executemany(
        "INSERT INTO exchange_rates (date, usd_sos, source) VALUES (?, ?, ?)",
        generate_exchange_rate_data(),
    )
    cursor.executemany(
        "INSERT INTO commodity_prices (date, commodity, price_usd, unit, city) VALUES (?, ?, ?, ?, ?)",
        generate_commodity_price_data(),
    )
    cursor.executemany(
        "INSERT INTO fuel_prices (date, fuel_type, price_usd, unit, city) VALUES (?, ?, ?, ?, ?)",
        generate_fuel_price_data(),
    )
    conn.commit()


def initialize_database() -> None:
    """
    Public entry point: create tables and seed sample data.
    Safe to call multiple times — idempotent.
    """
    conn = get_connection()
    try:
        create_tables(conn)
        seed_database(conn)
    finally:
        conn.close()
