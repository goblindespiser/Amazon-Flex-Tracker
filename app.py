from __future__ import annotations

import csv
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "Amazon Flex Tracker"
APP_DIR = Path.home() / ".flex_tracker_stage1"
DB_PATH = APP_DIR / "flex_tracker.db"
BACKUP_DIR = APP_DIR / "backups"
DATE_FMT = "%Y-%m-%d"
EXPENSE_CATEGORIES = (
    "Accessories",
    "Car Maintenance",
    "Delivery Equipment",
    "Equipment",
    "Miscellaneous",
    "Office/Printing",
    "Parking",
    "Phone/Service",
    "Supplies",
    "Tolls",
)


TAX_YEAR = 2026
DEFAULT_FILING_STATUS = "single"
TAX_DISCLAIMER = (
    "The app assumes Amazon Flex is the user's only income, assumes no withholding, "
    "no credits, no itemized deductions, no unusual adjustments, and no school district tax. "
    "The app uses the filing status you select and assumes you qualify for it. "
    "Dependent-related credits are not calculated."
)
TAX_SCOPE_NOTE = "Calculated using all logs through the selected month, including the selected month."

FILING_STATUS_LABELS = {
    "single": "Single",
    "married_filing_jointly": "Married Filing Jointly",
    "married_filing_separately": "Married Filing Separately",
    "head_of_household": "Head of Household",
    "qualifying_surviving_spouse": "Qualifying Surviving Spouse",
}

FEDERAL_STANDARD_DEDUCTION_CENTS = {
    "single": 1_610_000,
    "married_filing_jointly": 3_220_000,
    "married_filing_separately": 1_610_000,
    "head_of_household": 2_415_000,
    "qualifying_surviving_spouse": 3_220_000,
}

FEDERAL_BRACKETS_CENTS = {
    "single": [
        (1_240_000, Decimal("0.10")),
        (5_040_000, Decimal("0.12")),
        (10_570_000, Decimal("0.22")),
        (20_177_500, Decimal("0.24")),
        (25_622_500, Decimal("0.32")),
        (64_060_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    "married_filing_jointly": [
        (2_480_000, Decimal("0.10")),
        (10_080_000, Decimal("0.12")),
        (21_140_000, Decimal("0.22")),
        (40_355_000, Decimal("0.24")),
        (51_245_000, Decimal("0.32")),
        (76_870_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    "married_filing_separately": [
        (1_240_000, Decimal("0.10")),
        (5_040_000, Decimal("0.12")),
        (10_570_000, Decimal("0.22")),
        (20_177_500, Decimal("0.24")),
        (25_622_500, Decimal("0.32")),
        (38_435_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    "head_of_household": [
        (1_770_000, Decimal("0.10")),
        (6_745_000, Decimal("0.12")),
        (10_570_000, Decimal("0.22")),
        (20_175_000, Decimal("0.24")),
        (25_620_000, Decimal("0.32")),
        (64_060_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    "qualifying_surviving_spouse": [
        (2_480_000, Decimal("0.10")),
        (10_080_000, Decimal("0.12")),
        (21_140_000, Decimal("0.22")),
        (40_355_000, Decimal("0.24")),
        (51_245_000, Decimal("0.32")),
        (76_870_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
}

OHIO_BUSINESS_INCOME_DEDUCTION_LIMIT_CENTS = {
    "single": 25_000_000,
    "married_filing_jointly": 25_000_000,
    "married_filing_separately": 12_500_000,
    "head_of_household": 25_000_000,
    "qualifying_surviving_spouse": 25_000_000,
}

STANDARD_MILEAGE_RATE_PER_MILE = Decimal("0.725")
SE_NET_EARNINGS_FACTOR = Decimal("0.9235")
SE_SOCIAL_SECURITY_RATE = Decimal("0.124")
SE_MEDICARE_RATE = Decimal("0.029")
SE_THRESHOLD_CENTS = 40_000
SOCIAL_SECURITY_WAGE_BASE_CENTS = 18_450_000
OHIO_BUSINESS_TAX_RATE = Decimal("0.03")
OHIO_ESTIMATED_PAYMENT_THRESHOLD_CENTS = 50_000


# ----------------------------
# Helpers
# ----------------------------

def ensure_app_dirs() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_iso() -> str:
    return date.today().strftime(DATE_FMT)


def parse_non_negative_decimal_to_tenths(raw: str, field_name: str) -> int:
    raw = raw.strip()
    if not raw:
        return 0
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be a number.") from exc
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return int((value * Decimal("10")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def parse_non_negative_money_to_cents(raw: str, field_name: str) -> int:
    raw = raw.strip()
    if not raw:
        return 0
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be a valid dollar amount.") from exc
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return int((value * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def parse_date(raw: str, field_name: str) -> str:
    raw = raw.strip()
    if not raw:
        raise ValueError(f"{field_name} is required.")
    try:
        parsed = datetime.strptime(raw, DATE_FMT)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be in YYYY-MM-DD format.") from exc
    return parsed.strftime(DATE_FMT)


def tenths_to_str(value: int) -> str:
    return f"{Decimal(value) / Decimal('10'):.1f}"


def cents_to_str(value: int) -> str:
    return f"{Decimal(value) / Decimal('100'):.2f}"


def cents_to_currency(value: int) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${cents_to_str(abs(value))}"


def money_to_cents(value: Decimal) -> int:
    return int((value * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def month_range_for(month_str: str) -> tuple[str, str]:
    month_str = month_str.strip()
    dt = datetime.strptime(month_str, "%Y-%m")
    start = dt.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1, day=1)
    else:
        end = start.replace(month=start.month + 1, day=1)
    return start.strftime(DATE_FMT), end.strftime(DATE_FMT)




# ----------------------------
# Tax helpers
# ----------------------------

def calculate_progressive_tax_cents(taxable_income_cents: int, filing_status: str) -> int:
    taxable_income_cents = max(taxable_income_cents, 0)
    brackets = FEDERAL_BRACKETS_CENTS[filing_status]
    remaining = taxable_income_cents
    previous_cap = 0
    total = Decimal("0")

    for cap, rate in brackets:
        if remaining <= 0:
            break
        current_cap = taxable_income_cents if cap is None else min(taxable_income_cents, cap)
        if current_cap > previous_cap:
            bracket_amount = Decimal(current_cap - previous_cap) / Decimal("100")
            total += bracket_amount * rate
        previous_cap = current_cap

    return money_to_cents(total)


def calculate_tax_estimate(tax_basis: dict, filing_status: str) -> dict:
    gross_business_income_cents = tax_basis["gross_business_income_cents"]
    business_miles_tenths = tax_basis["business_miles_tenths"]
    deductible_tolls_parking_cents = tax_basis["tolls_parking_cents"]

    mileage_deduction_cents = money_to_cents((Decimal(business_miles_tenths) / Decimal("10")) * STANDARD_MILEAGE_RATE_PER_MILE)
    net_business_profit_cents = gross_business_income_cents - mileage_deduction_cents - deductible_tolls_parking_cents

    if net_business_profit_cents > 0:
        net_earnings_for_se_tax_cents = money_to_cents((Decimal(net_business_profit_cents) / Decimal("100")) * SE_NET_EARNINGS_FACTOR)
    else:
        net_earnings_for_se_tax_cents = 0

    if net_earnings_for_se_tax_cents >= SE_THRESHOLD_CENTS:
        ss_tax_base_cents = min(net_earnings_for_se_tax_cents, SOCIAL_SECURITY_WAGE_BASE_CENTS)
        ss_tax_cents = money_to_cents((Decimal(ss_tax_base_cents) / Decimal("100")) * SE_SOCIAL_SECURITY_RATE)
        medicare_tax_cents = money_to_cents((Decimal(net_earnings_for_se_tax_cents) / Decimal("100")) * SE_MEDICARE_RATE)
        estimated_self_employment_tax_cents = ss_tax_cents + medicare_tax_cents
        se_tax_status = "Self-employment tax applies"
    else:
        estimated_self_employment_tax_cents = 0
        se_tax_status = "Below self-employment tax threshold"

    deductible_half_se_tax_cents = estimated_self_employment_tax_cents // 2
    estimated_federal_agi_cents = net_business_profit_cents - deductible_half_se_tax_cents
    standard_deduction_cents = FEDERAL_STANDARD_DEDUCTION_CENTS[filing_status]
    estimated_federal_taxable_income_cents = max(estimated_federal_agi_cents - standard_deduction_cents, 0)
    estimated_federal_income_tax_cents = calculate_progressive_tax_cents(estimated_federal_taxable_income_cents, filing_status)
    estimated_total_federal_tax_cents = estimated_self_employment_tax_cents + estimated_federal_income_tax_cents

    ohio_starting_income_cents = max(estimated_federal_agi_cents, 0)
    ohio_business_income_deduction_cents = min(ohio_starting_income_cents, OHIO_BUSINESS_INCOME_DEDUCTION_LIMIT_CENTS[filing_status])
    ohio_taxable_business_income_cents = max(ohio_starting_income_cents - ohio_business_income_deduction_cents, 0)
    estimated_ohio_state_tax_cents = money_to_cents((Decimal(ohio_taxable_business_income_cents) / Decimal("100")) * OHIO_BUSINESS_TAX_RATE)
    ohio_status = (
        "Below Ohio estimated payment threshold"
        if estimated_ohio_state_tax_cents <= OHIO_ESTIMATED_PAYMENT_THRESHOLD_CENTS
        else "Ohio estimated payment threshold exceeded"
    )

    combined_estimated_tax_cents = estimated_total_federal_tax_cents + estimated_ohio_state_tax_cents

    return {
        "gross_business_income_cents": gross_business_income_cents,
        "mileage_deduction_cents": mileage_deduction_cents,
        "deductible_tolls_parking_cents": deductible_tolls_parking_cents,
        "net_business_profit_cents": net_business_profit_cents,
        "net_earnings_for_se_tax_cents": net_earnings_for_se_tax_cents,
        "estimated_self_employment_tax_cents": estimated_self_employment_tax_cents,
        "se_tax_status": se_tax_status,
        "deductible_half_se_tax_cents": deductible_half_se_tax_cents,
        "estimated_federal_agi_cents": estimated_federal_agi_cents,
        "standard_deduction_cents": standard_deduction_cents,
        "estimated_federal_taxable_income_cents": estimated_federal_taxable_income_cents,
        "estimated_federal_income_tax_cents": estimated_federal_income_tax_cents,
        "estimated_total_federal_tax_cents": estimated_total_federal_tax_cents,
        "ohio_starting_income_cents": ohio_starting_income_cents,
        "ohio_business_income_deduction_cents": ohio_business_income_deduction_cents,
        "ohio_taxable_business_income_cents": ohio_taxable_business_income_cents,
        "estimated_ohio_state_tax_cents": estimated_ohio_state_tax_cents,
        "ohio_status": ohio_status,
        "school_district_tax_status": "Excluded by assumption",
        "combined_estimated_tax_cents": combined_estimated_tax_cents,
    }


# ----------------------------
# Database
# ----------------------------

class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        ensure_app_dirs()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_date TEXT NOT NULL,
                    warehouse TEXT NOT NULL,
                    route_area TEXT NOT NULL,
                    route_hours_tenths INTEGER NOT NULL DEFAULT 0,
                    commute_to_pickup_tenths INTEGER NOT NULL DEFAULT 0,
                    commute_home_tenths INTEGER NOT NULL DEFAULT 0,
                    total_commute_tenths INTEGER NOT NULL DEFAULT 0,
                    route_start_odometer_tenths INTEGER NOT NULL DEFAULT 0,
                    route_stop_odometer_tenths INTEGER NOT NULL DEFAULT 0,
                    total_business_miles_tenths INTEGER NOT NULL DEFAULT 0,
                    tolls_parking_cents INTEGER NOT NULL DEFAULT 0,
                    gas_purchase_cents INTEGER NOT NULL DEFAULT 0,
                    total_block_pay_cents INTEGER NOT NULL DEFAULT 0,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS other_expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount_cents INTEGER NOT NULL DEFAULT 0,
                    description TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?)",
                ("filing_status", DEFAULT_FILING_STATUS),
            )
            conn.commit()

    def insert_daily_log(self, payload: dict) -> int:
        stamp = now_iso()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO daily_logs (
                    log_date, warehouse, route_area, route_hours_tenths,
                    commute_to_pickup_tenths, commute_home_tenths, total_commute_tenths,
                    route_start_odometer_tenths, route_stop_odometer_tenths, total_business_miles_tenths,
                    tolls_parking_cents, gas_purchase_cents, total_block_pay_cents, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["log_date"],
                    payload["warehouse"],
                    payload["route_area"],
                    payload["route_hours_tenths"],
                    payload["commute_to_pickup_tenths"],
                    payload["commute_home_tenths"],
                    payload["total_commute_tenths"],
                    payload["route_start_odometer_tenths"],
                    payload["route_stop_odometer_tenths"],
                    payload["total_business_miles_tenths"],
                    payload["tolls_parking_cents"],
                    payload["gas_purchase_cents"],
                    payload["total_block_pay_cents"],
                    payload["notes"],
                    stamp,
                    stamp,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_daily_log(self, log_id: int, payload: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE daily_logs
                SET log_date = ?, warehouse = ?, route_area = ?, route_hours_tenths = ?,
                    commute_to_pickup_tenths = ?, commute_home_tenths = ?, total_commute_tenths = ?,
                    route_start_odometer_tenths = ?, route_stop_odometer_tenths = ?, total_business_miles_tenths = ?,
                    tolls_parking_cents = ?, gas_purchase_cents = ?, total_block_pay_cents = ?, notes = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    payload["log_date"],
                    payload["warehouse"],
                    payload["route_area"],
                    payload["route_hours_tenths"],
                    payload["commute_to_pickup_tenths"],
                    payload["commute_home_tenths"],
                    payload["total_commute_tenths"],
                    payload["route_start_odometer_tenths"],
                    payload["route_stop_odometer_tenths"],
                    payload["total_business_miles_tenths"],
                    payload["tolls_parking_cents"],
                    payload["gas_purchase_cents"],
                    payload["total_block_pay_cents"],
                    payload["notes"],
                    now_iso(),
                    log_id,
                ),
            )
            conn.commit()

    def fetch_daily_logs(self, month_filter: str | None = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM daily_logs"
        params: tuple = ()
        if month_filter:
            start, end = month_range_for(month_filter)
            query += " WHERE log_date >= ? AND log_date < ?"
            params = (start, end)
        query += " ORDER BY log_date DESC, id DESC"
        with self._connect() as conn:
            return list(conn.execute(query, params).fetchall())

    def get_daily_log(self, log_id: int) -> sqlite3.Row | None:
        with self._connect() as conn:
            return conn.execute("SELECT * FROM daily_logs WHERE id = ?", (log_id,)).fetchone()

    def delete_daily_log(self, log_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM daily_logs WHERE id = ?", (log_id,))
            conn.commit()

    def insert_other_expense(self, payload: dict) -> int:
        stamp = now_iso()
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO other_expenses (
                    expense_date, category, amount_cents, description, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["expense_date"],
                    payload["category"],
                    payload["amount_cents"],
                    payload["description"],
                    payload["notes"],
                    stamp,
                    stamp,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def update_other_expense(self, expense_id: int, payload: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE other_expenses
                SET expense_date = ?, category = ?, amount_cents = ?, description = ?, notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    payload["expense_date"],
                    payload["category"],
                    payload["amount_cents"],
                    payload["description"],
                    payload["notes"],
                    now_iso(),
                    expense_id,
                ),
            )
            conn.commit()

    def fetch_other_expenses(self, month_filter: str | None = None) -> list[sqlite3.Row]:
        query = "SELECT * FROM other_expenses"
        params: tuple = ()
        if month_filter:
            start, end = month_range_for(month_filter)
            query += " WHERE expense_date >= ? AND expense_date < ?"
            params = (start, end)
        query += " ORDER BY expense_date DESC, id DESC"
        with self._connect() as conn:
            return list(conn.execute(query, params).fetchall())

    def get_other_expense(self, expense_id: int) -> sqlite3.Row | None:
        with self._connect() as conn:
            return conn.execute("SELECT * FROM other_expenses WHERE id = ?", (expense_id,)).fetchone()

    def delete_other_expense(self, expense_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM other_expenses WHERE id = ?", (expense_id,))
            conn.commit()


    def get_setting(self, key: str, default: str = "") -> str:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM app_settings WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO app_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
            conn.commit()

    def get_tax_basis(self, month_filter: str) -> dict:
        start_month, end_month = month_range_for(month_filter)
        year = datetime.strptime(month_filter, "%Y-%m").year
        year_start = f"{year}-01-01"
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    COALESCE(SUM(total_block_pay_cents), 0) AS gross_business_income_cents,
                    COALESCE(SUM(total_business_miles_tenths), 0) AS business_miles_tenths,
                    COALESCE(SUM(tolls_parking_cents), 0) AS tolls_parking_cents
                FROM daily_logs
                WHERE log_date >= ? AND log_date < ?
                """,
                (year_start, end_month),
            ).fetchone()
        return dict(row)

    def get_summary(self, month_filter: str | None = None) -> dict:
        def compute_derived(summary_row: dict) -> dict:
            total_miles_tenths = summary_row["business_miles_tenths"] + summary_row["total_commute_miles_tenths"]
            total_expenses_cents = (
                summary_row["tolls_parking_cents"]
                + summary_row["gas_purchase_cents"]
                + summary_row["other_expenses_cents"]
            )
            income_after_logged_expenses_cents = summary_row["gross_business_income_cents"] - total_expenses_cents
            return summary_row | {
                "total_miles_tenths": total_miles_tenths,
                "total_expenses_cents": total_expenses_cents,
                "income_after_logged_expenses_cents": income_after_logged_expenses_cents,
            }

        with self._connect() as conn:
            month_where = ""
            month_params: tuple = ()
            if month_filter:
                start, end = month_range_for(month_filter)
                month_where = " WHERE log_date >= ? AND log_date < ?"
                month_params = (start, end)

            row = conn.execute(
                f"""
                SELECT
                    COALESCE(SUM(total_block_pay_cents), 0) AS gross_business_income_cents,
                    COALESCE(SUM(total_business_miles_tenths), 0) AS business_miles_tenths,
                    COALESCE(SUM(commute_to_pickup_tenths), 0) AS commute_to_pickup_tenths,
                    COALESCE(SUM(commute_home_tenths), 0) AS commute_home_tenths,
                    COALESCE(SUM(total_commute_tenths), 0) AS total_commute_miles_tenths,
                    COALESCE(SUM(tolls_parking_cents), 0) AS tolls_parking_cents,
                    COALESCE(SUM(gas_purchase_cents), 0) AS gas_purchase_cents
                FROM daily_logs
                {month_where}
                """,
                month_params,
            ).fetchone()

            expense_where = ""
            expense_params: tuple = ()
            if month_filter:
                start, end = month_range_for(month_filter)
                expense_where = " WHERE expense_date >= ? AND expense_date < ?"
                expense_params = (start, end)

            expense_row = conn.execute(
                f"""
                SELECT COALESCE(SUM(amount_cents), 0) AS other_expenses_cents
                FROM other_expenses
                {expense_where}
                """,
                expense_params,
            ).fetchone()

            year = datetime.strptime(month_filter, "%Y-%m").year if month_filter else date.today().year
            year_start = f"{year}-01-01"
            year_end = f"{year + 1}-01-01"

            ytd_logs = conn.execute(
                """
                SELECT
                    COALESCE(SUM(total_block_pay_cents), 0) AS gross_business_income_cents,
                    COALESCE(SUM(total_business_miles_tenths), 0) AS business_miles_tenths,
                    COALESCE(SUM(commute_to_pickup_tenths), 0) AS commute_to_pickup_tenths,
                    COALESCE(SUM(commute_home_tenths), 0) AS commute_home_tenths,
                    COALESCE(SUM(total_commute_tenths), 0) AS total_commute_miles_tenths,
                    COALESCE(SUM(tolls_parking_cents), 0) AS tolls_parking_cents,
                    COALESCE(SUM(gas_purchase_cents), 0) AS gas_purchase_cents
                FROM daily_logs
                WHERE log_date >= ? AND log_date < ?
                """,
                (year_start, year_end),
            ).fetchone()

            ytd_exp = conn.execute(
                "SELECT COALESCE(SUM(amount_cents), 0) AS other_expenses_cents FROM other_expenses WHERE expense_date >= ? AND expense_date < ?",
                (year_start, year_end),
            ).fetchone()

        month_summary = dict(row) | {"other_expenses_cents": expense_row["other_expenses_cents"]}
        year_summary = dict(ytd_logs) | {"other_expenses_cents": ytd_exp["other_expenses_cents"]}
        return {
            "month": compute_derived(month_summary),
            "year": compute_derived(year_summary),
        }


# ----------------------------
# Validation helpers
# ----------------------------

def build_daily_log_payload(values: dict[str, str]) -> dict:
    log_date = parse_date(values["log_date"], "Date")
    warehouse = values["warehouse"].strip()
    route_area = values["route_area"].strip()
    if not warehouse:
        raise ValueError("Warehouse is required.")
    if not route_area:
        raise ValueError("Route Area is required.")

    route_hours_tenths = parse_non_negative_decimal_to_tenths(values["route_hours"], "Route Hours")
    commute_to_pickup_tenths = parse_non_negative_decimal_to_tenths(values["commute_to_pickup"], "Commute to Pickup")
    commute_home_tenths = parse_non_negative_decimal_to_tenths(values["commute_home"], "Commute Home")
    total_commute_tenths = commute_to_pickup_tenths + commute_home_tenths

    start_odo = parse_non_negative_decimal_to_tenths(values["route_start_odometer"], "Route Start Odometer")
    stop_odo = parse_non_negative_decimal_to_tenths(values["route_stop_odometer"], "Route Stop Odometer")
    if stop_odo < start_odo:
        raise ValueError("Route Stop Odometer cannot be lower than Route Start Odometer.")
    business_miles_tenths = stop_odo - start_odo

    return {
        "log_date": log_date,
        "warehouse": warehouse,
        "route_area": route_area,
        "route_hours_tenths": route_hours_tenths,
        "commute_to_pickup_tenths": commute_to_pickup_tenths,
        "commute_home_tenths": commute_home_tenths,
        "total_commute_tenths": total_commute_tenths,
        "route_start_odometer_tenths": start_odo,
        "route_stop_odometer_tenths": stop_odo,
        "total_business_miles_tenths": business_miles_tenths,
        "tolls_parking_cents": parse_non_negative_money_to_cents(values["tolls_parking"], "Tolls/Parking"),
        "gas_purchase_cents": parse_non_negative_money_to_cents(values["gas_purchase"], "Gas Purchase"),
        "total_block_pay_cents": parse_non_negative_money_to_cents(values["total_block_pay"], "Total Block Pay"),
        "notes": values["notes"].strip(),
    }


def build_other_expense_payload(values: dict[str, str]) -> dict:
    expense_date = parse_date(values["expense_date"], "Expense Date")
    category = values["category"].strip()
    if not category:
        raise ValueError("Category is required.")
    return {
        "expense_date": expense_date,
        "category": category,
        "amount_cents": parse_non_negative_money_to_cents(values["amount"], "Amount"),
        "description": values["description"].strip(),
        "notes": values["notes"].strip(),
    }


# ----------------------------
# UI
# ----------------------------

class FlexTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        ensure_app_dirs()
        self.db = Database(DB_PATH)
        self.title(APP_NAME)
        self.geometry("1400x860")
        self.minsize(1180, 760)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.status_var = tk.StringVar(value=f"Database: {DB_PATH}")

        self.daily_log_edit_id: int | None = None
        self.other_expense_edit_id: int | None = None
        self.tax_filing_status = self.db.get_setting("filing_status", DEFAULT_FILING_STATUS)

        self._build_ui()
        self.refresh_daily_logs()
        self.refresh_other_expenses()
        self.refresh_summary()
        self.refresh_tax_estimate()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.daily_logs_tab = ttk.Frame(notebook, padding=12)
        self.other_expenses_tab = ttk.Frame(notebook, padding=12)
        self.summary_tab = ttk.Frame(notebook, padding=12)
        self.tax_tab = ttk.Frame(notebook, padding=12)
        self.export_tab = ttk.Frame(notebook, padding=12)

        notebook.add(self.daily_logs_tab, text="Daily Logs")
        notebook.add(self.other_expenses_tab, text="Other Expenses")
        notebook.add(self.summary_tab, text="Summary")
        notebook.add(self.tax_tab, text="Tax Estimate")
        notebook.add(self.export_tab, text="Export & Backup")

        self._build_daily_logs_tab()
        self._build_other_expenses_tab()
        self._build_summary_tab()
        self._build_tax_tab()
        self._build_export_tab()

        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", padx=10, pady=(4, 10))

    # ---------------- Daily Logs ----------------
    def _build_daily_logs_tab(self) -> None:
        self.daily_vars = {
            "log_date": tk.StringVar(value=today_iso()),
            "warehouse": tk.StringVar(),
            "route_area": tk.StringVar(),
            "route_hours": tk.StringVar(),
            "commute_to_pickup": tk.StringVar(),
            "commute_home": tk.StringVar(),
            "total_commute": tk.StringVar(value="0.0"),
            "route_start_odometer": tk.StringVar(),
            "route_stop_odometer": tk.StringVar(),
            "total_business": tk.StringVar(value="0.0"),
            "tolls_parking": tk.StringVar(),
            "gas_purchase": tk.StringVar(),
            "total_block_pay": tk.StringVar(),
        }
        self.daily_notes = None

        for key in ("commute_to_pickup", "commute_home", "route_start_odometer", "route_stop_odometer"):
            self.daily_vars[key].trace_add("write", self._recompute_daily_derived)

        top = ttk.Panedwindow(self.daily_logs_tab, orient="horizontal")
        top.pack(fill="both", expand=True)

        form_frame = ttk.Labelframe(top, text="Daily Log Entry", padding=12)
        list_frame = ttk.Labelframe(top, text="Saved Logs", padding=12)
        top.add(form_frame, weight=1)
        top.add(list_frame, weight=2)

        fields = [
            ("Date", "log_date"),
            ("Warehouse", "warehouse"),
            ("Route Area", "route_area"),
            ("Route Hours", "route_hours"),
            ("Commute to Pickup", "commute_to_pickup"),
            ("Commute Home", "commute_home"),
            ("Total Commute Miles", "total_commute"),
            ("Route Start Odometer", "route_start_odometer"),
            ("Route Stop Odometer", "route_stop_odometer"),
            ("Total Business Miles", "total_business"),
            ("Tolls/Parking", "tolls_parking"),
            ("Gas Purchase", "gas_purchase"),
            ("Total Block Pay", "total_block_pay"),
        ]

        row = 0
        for label, key in fields:
            ttk.Label(form_frame, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))
            entry = ttk.Entry(form_frame, textvariable=self.daily_vars[key], width=28)
            if key in ("total_commute", "total_business"):
                entry.state(["readonly"])
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            row += 1

        ttk.Label(form_frame, text="Notes").grid(row=row, column=0, sticky="nw", pady=4, padx=(0, 10))
        self.daily_notes = tk.Text(form_frame, height=4, width=50)
        self.daily_notes.grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        btn_row = ttk.Frame(form_frame)
        btn_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(btn_row, text="Save Log", command=self.save_daily_log).pack(side="left")
        ttk.Button(btn_row, text="Clear Form", command=self.clear_daily_log_form).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Refresh List", command=self.refresh_daily_logs).pack(side="left")

        form_frame.columnconfigure(1, weight=1)

        filter_row = ttk.Frame(list_frame)
        filter_row.pack(fill="x", pady=(0, 8))
        ttk.Label(filter_row, text="Month Filter (YYYY-MM)").pack(side="left")
        self.daily_month_filter = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Entry(filter_row, textvariable=self.daily_month_filter, width=12).pack(side="left", padx=6)
        ttk.Button(filter_row, text="Apply", command=self.refresh_daily_logs).pack(side="left")
        ttk.Button(filter_row, text="Clear", command=self.clear_daily_month_filter).pack(side="left", padx=6)

        columns = (
            "id", "log_date", "warehouse", "route_area", "route_hours", "business_miles", "commute_miles", "block_pay"
        )
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill="both", expand=True)
        self.daily_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=22)
        headings = {
            "id": "ID",
            "log_date": "Date",
            "warehouse": "Warehouse",
            "route_area": "Route Area",
            "route_hours": "Hours",
            "business_miles": "Business Miles",
            "commute_miles": "Commute Miles",
            "block_pay": "Block Pay",
        }
        widths = {
            "id": 55,
            "log_date": 95,
            "warehouse": 155,
            "route_area": 155,
            "route_hours": 70,
            "business_miles": 100,
            "commute_miles": 105,
            "block_pay": 90,
        }
        for col in columns:
            self.daily_tree.heading(col, text=headings[col])
            self.daily_tree.column(col, width=widths[col], anchor="center", stretch=False)

        daily_y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.daily_tree.yview)
        daily_x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.daily_tree.xview)
        self.daily_tree.configure(yscrollcommand=daily_y_scroll.set, xscrollcommand=daily_x_scroll.set)

        self.daily_tree.grid(row=0, column=0, sticky="nsew")
        daily_y_scroll.grid(row=0, column=1, sticky="ns")
        daily_x_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.daily_tree.bind("<<TreeviewSelect>>", self.on_daily_log_selected)

        list_btns = ttk.Frame(list_frame)
        list_btns.pack(fill="x", pady=(8, 0))
        ttk.Button(list_btns, text="Load Selected", command=self.load_selected_daily_log).pack(side="left")
        ttk.Button(list_btns, text="Delete Selected", command=self.delete_selected_daily_log).pack(side="left", padx=6)

    def _recompute_daily_derived(self, *_args) -> None:
        try:
            commute_total = (
                parse_non_negative_decimal_to_tenths(self.daily_vars["commute_to_pickup"].get(), "Commute to Pickup")
                + parse_non_negative_decimal_to_tenths(self.daily_vars["commute_home"].get(), "Commute Home")
            )
            self.daily_vars["total_commute"].set(tenths_to_str(commute_total))
        except ValueError:
            self.daily_vars["total_commute"].set("0.0")

        try:
            start = parse_non_negative_decimal_to_tenths(self.daily_vars["route_start_odometer"].get(), "Route Start Odometer")
            stop = parse_non_negative_decimal_to_tenths(self.daily_vars["route_stop_odometer"].get(), "Route Stop Odometer")
            total = stop - start if stop >= start else 0
            self.daily_vars["total_business"].set(tenths_to_str(total))
        except ValueError:
            self.daily_vars["total_business"].set("0.0")

    def _get_daily_form_values(self) -> dict[str, str]:
        return {
            "log_date": self.daily_vars["log_date"].get(),
            "warehouse": self.daily_vars["warehouse"].get(),
            "route_area": self.daily_vars["route_area"].get(),
            "route_hours": self.daily_vars["route_hours"].get(),
            "commute_to_pickup": self.daily_vars["commute_to_pickup"].get(),
            "commute_home": self.daily_vars["commute_home"].get(),
            "route_start_odometer": self.daily_vars["route_start_odometer"].get(),
            "route_stop_odometer": self.daily_vars["route_stop_odometer"].get(),
            "tolls_parking": self.daily_vars["tolls_parking"].get(),
            "gas_purchase": self.daily_vars["gas_purchase"].get(),
            "total_block_pay": self.daily_vars["total_block_pay"].get(),
            "notes": self.daily_notes.get("1.0", "end").strip(),
        }

    def save_daily_log(self) -> None:
        try:
            payload = build_daily_log_payload(self._get_daily_form_values())
        except ValueError as exc:
            messagebox.showerror("Invalid Daily Log", str(exc))
            return

        if self.daily_log_edit_id is None:
            self.db.insert_daily_log(payload)
            self.status_var.set("Saved new daily log.")
        else:
            self.db.update_daily_log(self.daily_log_edit_id, payload)
            self.status_var.set(f"Updated daily log #{self.daily_log_edit_id}.")

        self.clear_daily_log_form()
        self.refresh_daily_logs()
        self.refresh_summary()
        self.refresh_tax_estimate()

    def clear_daily_log_form(self) -> None:
        self.daily_log_edit_id = None
        self.daily_vars["log_date"].set(today_iso())
        for key in (
            "warehouse", "route_area", "route_hours", "commute_to_pickup", "commute_home",
            "route_start_odometer", "route_stop_odometer", "tolls_parking", "gas_purchase", "total_block_pay"
        ):
            self.daily_vars[key].set("")
        self.daily_vars["total_commute"].set("0.0")
        self.daily_vars["total_business"].set("0.0")
        self.daily_notes.delete("1.0", "end")

    def clear_daily_month_filter(self) -> None:
        self.daily_month_filter.set("")
        self.refresh_daily_logs()

    def refresh_daily_logs(self) -> None:
        for item in self.daily_tree.get_children():
            self.daily_tree.delete(item)
        month_filter = self.daily_month_filter.get().strip() or None
        try:
            rows = self.db.fetch_daily_logs(month_filter=month_filter)
        except ValueError:
            messagebox.showerror("Invalid Month", "Daily log month filter must be YYYY-MM.")
            return
        for row in rows:
            self.daily_tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["id"],
                    row["log_date"],
                    row["warehouse"],
                    row["route_area"],
                    tenths_to_str(row["route_hours_tenths"]),
                    tenths_to_str(row["total_business_miles_tenths"]),
                    tenths_to_str(row["total_commute_tenths"]),
                    f"${cents_to_str(row['total_block_pay_cents'])}",
                ),
            )
        self.status_var.set(f"Loaded {len(rows)} daily log(s).")

    def on_daily_log_selected(self, _event=None) -> None:
        selected = self.daily_tree.selection()
        if selected:
            self.status_var.set(f"Selected daily log #{selected[0]}.")

    def load_selected_daily_log(self) -> None:
        selected = self.daily_tree.selection()
        if not selected:
            messagebox.showinfo("Load Daily Log", "Select a log first.")
            return
        log_id = int(selected[0])
        row = self.db.get_daily_log(log_id)
        if row is None:
            messagebox.showerror("Missing Log", "That log no longer exists.")
            self.refresh_daily_logs()
            return

        self.daily_log_edit_id = log_id
        self.daily_vars["log_date"].set(row["log_date"])
        self.daily_vars["warehouse"].set(row["warehouse"])
        self.daily_vars["route_area"].set(row["route_area"])
        self.daily_vars["route_hours"].set(tenths_to_str(row["route_hours_tenths"]))
        self.daily_vars["commute_to_pickup"].set(tenths_to_str(row["commute_to_pickup_tenths"]))
        self.daily_vars["commute_home"].set(tenths_to_str(row["commute_home_tenths"]))
        self.daily_vars["total_commute"].set(tenths_to_str(row["total_commute_tenths"]))
        self.daily_vars["route_start_odometer"].set(tenths_to_str(row["route_start_odometer_tenths"]))
        self.daily_vars["route_stop_odometer"].set(tenths_to_str(row["route_stop_odometer_tenths"]))
        self.daily_vars["total_business"].set(tenths_to_str(row["total_business_miles_tenths"]))
        self.daily_vars["tolls_parking"].set(cents_to_str(row["tolls_parking_cents"]))
        self.daily_vars["gas_purchase"].set(cents_to_str(row["gas_purchase_cents"]))
        self.daily_vars["total_block_pay"].set(cents_to_str(row["total_block_pay_cents"]))
        self.daily_notes.delete("1.0", "end")
        self.daily_notes.insert("1.0", row["notes"])
        self.status_var.set(f"Loaded daily log #{log_id} into form.")

    def delete_selected_daily_log(self) -> None:
        selected = self.daily_tree.selection()
        if not selected:
            messagebox.showinfo("Delete Daily Log", "Select a log first.")
            return
        log_id = int(selected[0])
        if not messagebox.askyesno("Delete Daily Log", f"Delete daily log #{log_id}?"):
            return
        self.db.delete_daily_log(log_id)
        if self.daily_log_edit_id == log_id:
            self.clear_daily_log_form()
        self.refresh_daily_logs()
        self.refresh_summary()
        self.refresh_tax_estimate()
        self.status_var.set(f"Deleted daily log #{log_id}.")

    # ---------------- Other Expenses ----------------
    def _build_other_expenses_tab(self) -> None:
        self.expense_vars = {
            "expense_date": tk.StringVar(value=today_iso()),
            "category": tk.StringVar(),
            "amount": tk.StringVar(),
            "description": tk.StringVar(),
        }
        self.expense_notes = None

        top = ttk.Panedwindow(self.other_expenses_tab, orient="horizontal")
        top.pack(fill="both", expand=True)

        form_frame = ttk.Labelframe(top, text="Other Expense Entry", padding=12)
        list_frame = ttk.Labelframe(top, text="Saved Other Expenses", padding=12)
        top.add(form_frame, weight=1)
        top.add(list_frame, weight=2)

        row = 0

        ttk.Label(form_frame, text="Expense Date").grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))
        ttk.Entry(form_frame, textvariable=self.expense_vars["expense_date"], width=28).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        ttk.Label(form_frame, text="Category").grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))
        self.expense_category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.expense_vars["category"],
            values=EXPENSE_CATEGORIES,
            state="readonly",
            width=26,
        )
        self.expense_category_combo.grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        ttk.Label(form_frame, text="Amount").grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))
        ttk.Entry(form_frame, textvariable=self.expense_vars["amount"], width=28).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        ttk.Label(form_frame, text="Description").grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))
        ttk.Entry(form_frame, textvariable=self.expense_vars["description"], width=28).grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        ttk.Label(form_frame, text="Notes").grid(row=row, column=0, sticky="nw", pady=4, padx=(0, 10))
        self.expense_notes = tk.Text(form_frame, height=4, width=50)
        self.expense_notes.grid(row=row, column=1, sticky="ew", pady=4)
        row += 1

        btn_row = ttk.Frame(form_frame)
        btn_row.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(btn_row, text="Save Expense", command=self.save_other_expense).pack(side="left")
        ttk.Button(btn_row, text="Clear Form", command=self.clear_other_expense_form).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Refresh List", command=self.refresh_other_expenses).pack(side="left")

        form_frame.columnconfigure(1, weight=1)

        filter_row = ttk.Frame(list_frame)
        filter_row.pack(fill="x", pady=(0, 8))
        ttk.Label(filter_row, text="Month Filter (YYYY-MM)").pack(side="left")
        self.expense_month_filter = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Entry(filter_row, textvariable=self.expense_month_filter, width=12).pack(side="left", padx=6)
        ttk.Button(filter_row, text="Apply", command=self.refresh_other_expenses).pack(side="left")
        ttk.Button(filter_row, text="Clear", command=self.clear_other_expense_month_filter).pack(side="left", padx=6)

        columns = ("id", "expense_date", "category", "amount", "description")
        expense_tree_frame = ttk.Frame(list_frame)
        expense_tree_frame.pack(fill="both", expand=True)
        self.expense_tree = ttk.Treeview(expense_tree_frame, columns=columns, show="headings", height=22)
        headings = {
            "id": "ID",
            "expense_date": "Date",
            "category": "Category",
            "amount": "Amount",
            "description": "Description",
        }
        widths = {"id": 55, "expense_date": 95, "category": 140, "amount": 90, "description": 320}
        for col in columns:
            self.expense_tree.heading(col, text=headings[col])
            self.expense_tree.column(col, width=widths[col], anchor="center", stretch=False)

        expense_y_scroll = ttk.Scrollbar(expense_tree_frame, orient="vertical", command=self.expense_tree.yview)
        expense_x_scroll = ttk.Scrollbar(expense_tree_frame, orient="horizontal", command=self.expense_tree.xview)
        self.expense_tree.configure(yscrollcommand=expense_y_scroll.set, xscrollcommand=expense_x_scroll.set)

        self.expense_tree.grid(row=0, column=0, sticky="nsew")
        expense_y_scroll.grid(row=0, column=1, sticky="ns")
        expense_x_scroll.grid(row=1, column=0, sticky="ew")
        expense_tree_frame.rowconfigure(0, weight=1)
        expense_tree_frame.columnconfigure(0, weight=1)
        self.expense_tree.bind("<<TreeviewSelect>>", self.on_other_expense_selected)

        list_btns = ttk.Frame(list_frame)
        list_btns.pack(fill="x", pady=(8, 0))
        ttk.Button(list_btns, text="Load Selected", command=self.load_selected_other_expense).pack(side="left")
        ttk.Button(list_btns, text="Delete Selected", command=self.delete_selected_other_expense).pack(side="left", padx=6)

    def _get_other_expense_form_values(self) -> dict[str, str]:
        return {
            "expense_date": self.expense_vars["expense_date"].get(),
            "category": self.expense_vars["category"].get(),
            "amount": self.expense_vars["amount"].get(),
            "description": self.expense_vars["description"].get(),
            "notes": self.expense_notes.get("1.0", "end").strip(),
        }

    def save_other_expense(self) -> None:
        try:
            payload = build_other_expense_payload(self._get_other_expense_form_values())
        except ValueError as exc:
            messagebox.showerror("Invalid Other Expense", str(exc))
            return

        if self.other_expense_edit_id is None:
            self.db.insert_other_expense(payload)
            self.status_var.set("Saved new other expense.")
        else:
            self.db.update_other_expense(self.other_expense_edit_id, payload)
            self.status_var.set(f"Updated other expense #{self.other_expense_edit_id}.")

        self.clear_other_expense_form()
        self.refresh_other_expenses()
        self.refresh_summary()

    def clear_other_expense_form(self) -> None:
        self.other_expense_edit_id = None
        self.expense_vars["expense_date"].set(today_iso())
        self.expense_vars["category"].set("")
        self.expense_vars["amount"].set("")
        self.expense_vars["description"].set("")
        self.expense_notes.delete("1.0", "end")

    def clear_other_expense_month_filter(self) -> None:
        self.expense_month_filter.set("")
        self.refresh_other_expenses()

    def refresh_other_expenses(self) -> None:
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        month_filter = self.expense_month_filter.get().strip() or None
        try:
            rows = self.db.fetch_other_expenses(month_filter=month_filter)
        except ValueError:
            messagebox.showerror("Invalid Month", "Other expense month filter must be YYYY-MM.")
            return
        for row in rows:
            self.expense_tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(
                    row["id"],
                    row["expense_date"],
                    row["category"],
                    f"${cents_to_str(row['amount_cents'])}",
                    row["description"],
                ),
            )
        self.status_var.set(f"Loaded {len(rows)} other expense(s).")

    def on_other_expense_selected(self, _event=None) -> None:
        selected = self.expense_tree.selection()
        if selected:
            self.status_var.set(f"Selected other expense #{selected[0]}.")

    def load_selected_other_expense(self) -> None:
        selected = self.expense_tree.selection()
        if not selected:
            messagebox.showinfo("Load Other Expense", "Select an expense first.")
            return
        expense_id = int(selected[0])
        row = self.db.get_other_expense(expense_id)
        if row is None:
            messagebox.showerror("Missing Expense", "That expense no longer exists.")
            self.refresh_other_expenses()
            return

        self.other_expense_edit_id = expense_id
        self.expense_vars["expense_date"].set(row["expense_date"])
        self.expense_vars["category"].set(row["category"])
        self.expense_vars["amount"].set(cents_to_str(row["amount_cents"]))
        self.expense_vars["description"].set(row["description"])
        self.expense_notes.delete("1.0", "end")
        self.expense_notes.insert("1.0", row["notes"])
        self.status_var.set(f"Loaded other expense #{expense_id} into form.")

    def delete_selected_other_expense(self) -> None:
        selected = self.expense_tree.selection()
        if not selected:
            messagebox.showinfo("Delete Other Expense", "Select an expense first.")
            return
        expense_id = int(selected[0])
        if not messagebox.askyesno("Delete Other Expense", f"Delete other expense #{expense_id}?"):
            return
        self.db.delete_other_expense(expense_id)
        if self.other_expense_edit_id == expense_id:
            self.clear_other_expense_form()
        self.refresh_other_expenses()
        self.refresh_summary()
        self.status_var.set(f"Deleted other expense #{expense_id}.")

    # ---------------- Summary ----------------
    def _build_summary_tab(self) -> None:
        top = ttk.Frame(self.summary_tab)
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="Summary Month (YYYY-MM)").pack(side="left")
        self.summary_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Entry(top, textvariable=self.summary_month_var, width=12).pack(side="left", padx=6)
        ttk.Button(top, text="Refresh Summary", command=self.refresh_summary).pack(side="left")
        ttk.Button(top, text="Use Current Month", command=self.set_summary_current_month).pack(side="left", padx=6)

        body = ttk.Frame(self.summary_tab)
        body.pack(fill="both", expand=True)

        self.month_summary_frame = ttk.Labelframe(body, text="Month to Date", padding=12)
        self.year_summary_frame = ttk.Labelframe(body, text="Year to Date", padding=12)
        self.month_summary_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.year_summary_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self.month_summary_labels: dict[str, tk.StringVar] = {}
        self.year_summary_labels: dict[str, tk.StringVar] = {}
        self.summary_keys = (
            "Business Miles",
            "Commute to Pickup",
            "Commute Home",
            "Total Commute Miles",
            "Total Miles",
            "Tolls/Parking",
            "Gas Purchases",
            "Other Expenses",
            "Total Expenses",
            "Gross Business Income",
            "Income After Logged Expenses",
        )

        for container, label_map in ((self.month_summary_frame, self.month_summary_labels), (self.year_summary_frame, self.year_summary_labels)):
            for idx, key in enumerate(self.summary_keys):
                label_map[key] = tk.StringVar(value="0")
                ttk.Label(container, text=key).grid(row=idx, column=0, sticky="w", pady=6, padx=(0, 12))
                ttk.Label(container, textvariable=label_map[key]).grid(row=idx, column=1, sticky="e", pady=6)
            container.columnconfigure(1, weight=1)

    def set_summary_current_month(self) -> None:
        self.summary_month_var.set(date.today().strftime("%Y-%m"))
        self.refresh_summary()

    def refresh_summary(self) -> None:
        month_filter = self.summary_month_var.get().strip() or date.today().strftime("%Y-%m")
        try:
            summary = self.db.get_summary(month_filter=month_filter)
        except ValueError:
            messagebox.showerror("Invalid Month", "Summary month must be YYYY-MM.")
            return

        month = summary["month"]
        year = summary["year"]

        self.month_summary_labels["Business Miles"].set(tenths_to_str(month["business_miles_tenths"]))
        self.month_summary_labels["Commute to Pickup"].set(tenths_to_str(month["commute_to_pickup_tenths"]))
        self.month_summary_labels["Commute Home"].set(tenths_to_str(month["commute_home_tenths"]))
        self.month_summary_labels["Total Commute Miles"].set(tenths_to_str(month["total_commute_miles_tenths"]))
        self.month_summary_labels["Total Miles"].set(tenths_to_str(month["total_miles_tenths"]))
        self.month_summary_labels["Tolls/Parking"].set(f"${cents_to_str(month['tolls_parking_cents'])}")
        self.month_summary_labels["Gas Purchases"].set(f"${cents_to_str(month['gas_purchase_cents'])}")
        self.month_summary_labels["Other Expenses"].set(f"${cents_to_str(month['other_expenses_cents'])}")
        self.month_summary_labels["Total Expenses"].set(f"${cents_to_str(month['total_expenses_cents'])}")
        self.month_summary_labels["Gross Business Income"].set(f"${cents_to_str(month['gross_business_income_cents'])}")
        self.month_summary_labels["Income After Logged Expenses"].set(f"${cents_to_str(month['income_after_logged_expenses_cents'])}")

        self.year_summary_labels["Business Miles"].set(tenths_to_str(year["business_miles_tenths"]))
        self.year_summary_labels["Commute to Pickup"].set(tenths_to_str(year["commute_to_pickup_tenths"]))
        self.year_summary_labels["Commute Home"].set(tenths_to_str(year["commute_home_tenths"]))
        self.year_summary_labels["Total Commute Miles"].set(tenths_to_str(year["total_commute_miles_tenths"]))
        self.year_summary_labels["Total Miles"].set(tenths_to_str(year["total_miles_tenths"]))
        self.year_summary_labels["Tolls/Parking"].set(f"${cents_to_str(year['tolls_parking_cents'])}")
        self.year_summary_labels["Gas Purchases"].set(f"${cents_to_str(year['gas_purchase_cents'])}")
        self.year_summary_labels["Other Expenses"].set(f"${cents_to_str(year['other_expenses_cents'])}")
        self.year_summary_labels["Total Expenses"].set(f"${cents_to_str(year['total_expenses_cents'])}")
        self.year_summary_labels["Gross Business Income"].set(f"${cents_to_str(year['gross_business_income_cents'])}")
        self.year_summary_labels["Income After Logged Expenses"].set(f"${cents_to_str(year['income_after_logged_expenses_cents'])}")

        self.status_var.set(f"Refreshed summary for {month_filter}.")



    # ---------------- Tax Estimate ----------------
    def _build_tax_tab(self) -> None:
        outer = ttk.Frame(self.tax_tab)
        outer.pack(fill="both", expand=True)

        self.tax_canvas = tk.Canvas(outer, highlightthickness=0)
        tax_scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.tax_canvas.yview)
        self.tax_canvas.configure(yscrollcommand=tax_scrollbar.set)

        tax_scrollbar.pack(side="right", fill="y")
        self.tax_canvas.pack(side="left", fill="both", expand=True)

        self.tax_content = ttk.Frame(self.tax_canvas)
        self.tax_canvas_window = self.tax_canvas.create_window((0, 0), window=self.tax_content, anchor="nw")

        def _configure_tax_scroll_region(event: tk.Event) -> None:
            self.tax_canvas.configure(scrollregion=self.tax_canvas.bbox("all"))

        def _configure_tax_canvas_width(event: tk.Event) -> None:
            self.tax_canvas.itemconfigure(self.tax_canvas_window, width=event.width)

        self.tax_content.bind("<Configure>", _configure_tax_scroll_region)
        self.tax_canvas.bind("<Configure>", _configure_tax_canvas_width)

        def _on_mousewheel(event: tk.Event) -> None:
            self.tax_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(_event: tk.Event) -> None:
            self.tax_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(_event: tk.Event) -> None:
            self.tax_canvas.unbind_all("<MouseWheel>")

        self.tax_canvas.bind("<Enter>", _bind_mousewheel)
        self.tax_canvas.bind("<Leave>", _unbind_mousewheel)

        controls = ttk.Frame(self.tax_content)
        controls.pack(fill="x", pady=(0, 12))

        ttk.Label(controls, text="Tax Month (YYYY-MM)").pack(side="left")
        self.tax_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Entry(controls, textvariable=self.tax_month_var, width=12).pack(side="left", padx=6)
        ttk.Button(controls, text="Refresh Tax Estimate", command=self.refresh_tax_estimate).pack(side="left")
        ttk.Button(controls, text="Use Current Month", command=self.set_tax_current_month).pack(side="left", padx=6)
        ttk.Button(controls, text="Tax Settings", command=self.open_tax_settings).pack(side="left")

        assumptions = ttk.Frame(self.tax_content)
        assumptions.pack(fill="x", pady=(0, 6))
        self.tax_year_label_var = tk.StringVar(value=f"Tax Year: {TAX_YEAR}")
        self.tax_filing_status_label_var = tk.StringVar(value=f"Filing Status: {FILING_STATUS_LABELS[self.tax_filing_status]}")
        self.tax_basis_label_var = tk.StringVar(value="Basis: If the tax year ended today")
        ttk.Label(assumptions, textvariable=self.tax_year_label_var).pack(side="left", padx=(0, 16))
        ttk.Label(assumptions, textvariable=self.tax_filing_status_label_var).pack(side="left", padx=(0, 16))
        ttk.Label(assumptions, textvariable=self.tax_basis_label_var).pack(side="left")

        ttk.Label(self.tax_content, text=TAX_SCOPE_NOTE).pack(anchor="w", pady=(0, 4))
        ttk.Label(self.tax_content, text=TAX_DISCLAIMER, wraplength=1250, justify="left").pack(anchor="w", pady=(0, 12))

        self.federal_tax_frame = ttk.Labelframe(self.tax_content, text="Federal Estimate (Flex Only)", padding=12)
        self.ohio_tax_frame = ttk.Labelframe(self.tax_content, text="Ohio Estimate (State Only)", padding=12)
        self.combined_tax_frame = ttk.Labelframe(self.tax_content, text="Combined Estimated Tax", padding=12)
        self.federal_tax_frame.pack(fill="x", pady=(0, 10))
        self.ohio_tax_frame.pack(fill="x", pady=(0, 10))
        self.combined_tax_frame.pack(fill="x")

        self.federal_tax_labels = {}
        self.ohio_tax_labels = {}
        self.combined_tax_labels = {}

        self.federal_tax_keys = (
            "Gross Business Income",
            "Mileage Deduction",
            "Deductible Tolls/Parking",
            "Net Business Profit",
            "Net Earnings for SE Tax",
            "Estimated Self-Employment Tax",
            "SE Tax Status",
            "Deductible Half of SE Tax",
            "Estimated Federal AGI",
            "Standard Deduction",
            "Estimated Federal Taxable Income",
            "Estimated Federal Income Tax",
            "Estimated Total Federal Tax",
        )
        self.ohio_tax_keys = (
            "Ohio Starting Income",
            "Ohio Business Income Deduction",
            "Ohio Taxable Business Income",
            "Estimated Ohio State Tax",
            "Ohio Status",
            "School District Tax",
        )
        self.combined_tax_keys = (
            "Estimated Total Federal Tax",
            "Estimated Ohio State Tax",
            "Combined Estimated Tax",
        )

        for container, keys, label_map in (
            (self.federal_tax_frame, self.federal_tax_keys, self.federal_tax_labels),
            (self.ohio_tax_frame, self.ohio_tax_keys, self.ohio_tax_labels),
            (self.combined_tax_frame, self.combined_tax_keys, self.combined_tax_labels),
        ):
            for idx, key in enumerate(keys):
                label_map[key] = tk.StringVar(value="")
                ttk.Label(container, text=key).grid(row=idx, column=0, sticky="w", pady=4, padx=(0, 12))
                ttk.Label(container, textvariable=label_map[key]).grid(row=idx, column=1, sticky="e", pady=4)
            container.columnconfigure(1, weight=1)

    def set_tax_current_month(self) -> None:
        self.tax_month_var.set(date.today().strftime("%Y-%m"))
        self.refresh_tax_estimate()

    def open_tax_settings(self) -> None:
        window = tk.Toplevel(self)
        window.title("Tax Settings")
        window.transient(self)
        window.grab_set()
        window.resizable(False, False)

        frame = ttk.Frame(window, padding=14)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Tax Year:").grid(row=0, column=0, sticky="w", pady=4, padx=(0, 10))
        tax_year_var = tk.StringVar(value=str(TAX_YEAR))
        year_entry = ttk.Entry(frame, textvariable=tax_year_var, width=18)
        year_entry.state(["readonly"])
        year_entry.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(frame, text="Filing Status:").grid(row=1, column=0, sticky="w", pady=4, padx=(0, 10))
        filing_status_var = tk.StringVar(value=FILING_STATUS_LABELS[self.tax_filing_status])
        filing_status_combo = ttk.Combobox(
            frame,
            textvariable=filing_status_var,
            values=tuple(FILING_STATUS_LABELS.values()),
            state="readonly",
            width=28,
        )
        filing_status_combo.grid(row=1, column=1, sticky="ew", pady=4)

        assumptions_box = ttk.Labelframe(frame, text="Assumptions", padding=10)
        assumptions_box.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 8))
        assumptions_text = (
            "Estimate Basis: If the tax year ended today\n"
            "Income Source: Amazon Flex only\n"
            "Deduction Method: Standard mileage\n"
            "Federal Withholding: Assumed $0\n"
            "Credits: Assumed $0\n"
            "Itemized Deductions: Not used\n"
            "Unusual Adjustments: Not used\n"
            "School District Tax: Excluded"
        )
        ttk.Label(assumptions_box, text=assumptions_text, justify="left").pack(anchor="w")

        disclaimer_box = ttk.Labelframe(frame, text="Disclaimer", padding=10)
        disclaimer_box.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(disclaimer_box, text=TAX_DISCLAIMER, wraplength=520, justify="left").pack(anchor="w")

        btn_row = ttk.Frame(frame)
        btn_row.grid(row=4, column=0, columnspan=2, sticky="e")

        def save_settings() -> None:
            reverse_map = {label: key for key, label in FILING_STATUS_LABELS.items()}
            selected_key = reverse_map[filing_status_var.get()]
            self.tax_filing_status = selected_key
            self.db.set_setting("filing_status", selected_key)
            self.tax_filing_status_label_var.set(f"Filing Status: {FILING_STATUS_LABELS[selected_key]}")
            self.refresh_tax_estimate()
            self.status_var.set("Saved tax settings.")
            window.destroy()

        ttk.Button(btn_row, text="Save", command=save_settings).pack(side="left")
        ttk.Button(btn_row, text="Cancel", command=window.destroy).pack(side="left", padx=6)

        frame.columnconfigure(1, weight=1)

    def refresh_tax_estimate(self) -> None:
        month_filter = self.tax_month_var.get().strip() or date.today().strftime("%Y-%m")
        try:
            tax_basis = self.db.get_tax_basis(month_filter)
        except ValueError:
            messagebox.showerror("Invalid Month", "Tax month must be YYYY-MM.")
            return

        results = calculate_tax_estimate(tax_basis, self.tax_filing_status)

        federal_mapping = {
            "Gross Business Income": results["gross_business_income_cents"],
            "Mileage Deduction": results["mileage_deduction_cents"],
            "Deductible Tolls/Parking": results["deductible_tolls_parking_cents"],
            "Net Business Profit": results["net_business_profit_cents"],
            "Net Earnings for SE Tax": results["net_earnings_for_se_tax_cents"],
            "Estimated Self-Employment Tax": results["estimated_self_employment_tax_cents"],
            "SE Tax Status": results["se_tax_status"],
            "Deductible Half of SE Tax": results["deductible_half_se_tax_cents"],
            "Estimated Federal AGI": results["estimated_federal_agi_cents"],
            "Standard Deduction": results["standard_deduction_cents"],
            "Estimated Federal Taxable Income": results["estimated_federal_taxable_income_cents"],
            "Estimated Federal Income Tax": results["estimated_federal_income_tax_cents"],
            "Estimated Total Federal Tax": results["estimated_total_federal_tax_cents"],
        }
        ohio_mapping = {
            "Ohio Starting Income": results["ohio_starting_income_cents"],
            "Ohio Business Income Deduction": results["ohio_business_income_deduction_cents"],
            "Ohio Taxable Business Income": results["ohio_taxable_business_income_cents"],
            "Estimated Ohio State Tax": results["estimated_ohio_state_tax_cents"],
            "Ohio Status": results["ohio_status"],
            "School District Tax": results["school_district_tax_status"],
        }
        combined_mapping = {
            "Estimated Total Federal Tax": results["estimated_total_federal_tax_cents"],
            "Estimated Ohio State Tax": results["estimated_ohio_state_tax_cents"],
            "Combined Estimated Tax": results["combined_estimated_tax_cents"],
        }

        for key in self.federal_tax_keys:
            value = federal_mapping[key]
            self.federal_tax_labels[key].set(cents_to_currency(value) if isinstance(value, int) else str(value))
        for key in self.ohio_tax_keys:
            value = ohio_mapping[key]
            self.ohio_tax_labels[key].set(cents_to_currency(value) if isinstance(value, int) else str(value))
        for key in self.combined_tax_keys:
            value = combined_mapping[key]
            self.combined_tax_labels[key].set(cents_to_currency(value) if isinstance(value, int) else str(value))

        self.status_var.set(f"Refreshed tax estimate for {month_filter}.")

    # ---------------- Export and Backup ----------------
    def _build_export_tab(self) -> None:
        frame = ttk.Frame(self.export_tab)
        frame.pack(fill="both", expand=True)

        export_logs_box = ttk.Labelframe(frame, text="Export Daily Logs", padding=12)
        export_exp_box = ttk.Labelframe(frame, text="Export Other Expenses", padding=12)
        export_summary_box = ttk.Labelframe(frame, text="Export Summary", padding=12)
        export_tax_box = ttk.Labelframe(frame, text="Export Tax Estimate", padding=12)
        backup_box = ttk.Labelframe(frame, text="Local Backup", padding=12)

        export_logs_box.pack(fill="x", pady=(0, 10))
        export_exp_box.pack(fill="x", pady=(0, 10))
        export_summary_box.pack(fill="x", pady=(0, 10))
        export_tax_box.pack(fill="x", pady=(0, 10))
        backup_box.pack(fill="x")

        self.export_logs_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Label(export_logs_box, text="Month Filter (optional, YYYY-MM)").pack(side="left")
        ttk.Entry(export_logs_box, textvariable=self.export_logs_month_var, width=12).pack(side="left", padx=6)
        ttk.Button(export_logs_box, text="Export Daily Logs CSV", command=self.export_daily_logs_csv).pack(side="left", padx=6)

        self.export_expenses_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Label(export_exp_box, text="Month Filter (optional, YYYY-MM)").pack(side="left")
        ttk.Entry(export_exp_box, textvariable=self.export_expenses_month_var, width=12).pack(side="left", padx=6)
        ttk.Button(export_exp_box, text="Export Other Expenses CSV", command=self.export_other_expenses_csv).pack(side="left", padx=6)

        self.export_summary_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Label(export_summary_box, text="Summary Month (YYYY-MM)").pack(side="left")
        ttk.Entry(export_summary_box, textvariable=self.export_summary_month_var, width=12).pack(side="left", padx=6)
        ttk.Button(export_summary_box, text="Export Summary CSV", command=self.export_summary_csv).pack(side="left", padx=6)

        self.export_tax_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Label(export_tax_box, text="Tax Month (YYYY-MM)").pack(side="left")
        ttk.Entry(export_tax_box, textvariable=self.export_tax_month_var, width=12).pack(side="left", padx=6)
        ttk.Button(export_tax_box, text="Export Tax Estimate CSV", command=self.export_tax_estimate_csv).pack(side="left", padx=6)

        ttk.Label(backup_box, text=f"Database Path: {DB_PATH}").pack(anchor="w")
        ttk.Label(backup_box, text=f"Default Backup Folder: {BACKUP_DIR}").pack(anchor="w", pady=(6, 6))
        ttk.Button(backup_box, text="Create Timestamped Backup", command=self.create_backup).pack(anchor="w")

    def export_daily_logs_csv(self) -> None:
        month_filter = self.export_logs_month_var.get().strip() or None
        try:
            rows = self.db.fetch_daily_logs(month_filter=month_filter)
        except ValueError:
            messagebox.showerror("Invalid Month", "Export month must be YYYY-MM.")
            return
        if not rows:
            messagebox.showinfo("Export Daily Logs", "There are no daily logs to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Daily Logs CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="daily_logs.csv",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "log_date", "warehouse", "route_area", "route_hours", "commute_to_pickup",
                "commute_home", "total_commute_miles", "route_start_odometer", "route_stop_odometer",
                "total_business_miles", "tolls_parking", "gas_purchase", "total_block_pay", "notes",
                "created_at", "updated_at",
            ])
            for row in rows:
                writer.writerow([
                    row["id"],
                    row["log_date"],
                    row["warehouse"],
                    row["route_area"],
                    tenths_to_str(row["route_hours_tenths"]),
                    tenths_to_str(row["commute_to_pickup_tenths"]),
                    tenths_to_str(row["commute_home_tenths"]),
                    tenths_to_str(row["total_commute_tenths"]),
                    tenths_to_str(row["route_start_odometer_tenths"]),
                    tenths_to_str(row["route_stop_odometer_tenths"]),
                    tenths_to_str(row["total_business_miles_tenths"]),
                    cents_to_str(row["tolls_parking_cents"]),
                    cents_to_str(row["gas_purchase_cents"]),
                    cents_to_str(row["total_block_pay_cents"]),
                    row["notes"],
                    row["created_at"],
                    row["updated_at"],
                ])
        self.status_var.set(f"Exported daily logs to {path}.")
        messagebox.showinfo("Export Daily Logs", f"Exported {len(rows)} daily log(s).")

    def export_other_expenses_csv(self) -> None:
        month_filter = self.export_expenses_month_var.get().strip() or None
        try:
            rows = self.db.fetch_other_expenses(month_filter=month_filter)
        except ValueError:
            messagebox.showerror("Invalid Month", "Export month must be YYYY-MM.")
            return
        if not rows:
            messagebox.showinfo("Export Other Expenses", "There are no other expenses to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Other Expenses CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="other_expenses.csv",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id", "expense_date", "category", "amount", "description", "notes", "created_at", "updated_at"
            ])
            for row in rows:
                writer.writerow([
                    row["id"],
                    row["expense_date"],
                    row["category"],
                    cents_to_str(row["amount_cents"]),
                    row["description"],
                    row["notes"],
                    row["created_at"],
                    row["updated_at"],
                ])
        self.status_var.set(f"Exported other expenses to {path}.")
        messagebox.showinfo("Export Other Expenses", f"Exported {len(rows)} expense(s).")

    def export_summary_csv(self) -> None:
        month_filter = self.export_summary_month_var.get().strip() or date.today().strftime("%Y-%m")
        try:
            summary = self.db.get_summary(month_filter=month_filter)
        except ValueError:
            messagebox.showerror("Invalid Month", "Summary export month must be YYYY-MM.")
            return

        path = filedialog.asksaveasfilename(
            title="Save Summary CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"summary_{month_filter}.csv",
        )
        if not path:
            return

        label_to_key = {
            "Business Miles": "business_miles_tenths",
            "Commute to Pickup": "commute_to_pickup_tenths",
            "Commute Home": "commute_home_tenths",
            "Total Commute Miles": "total_commute_miles_tenths",
            "Total Miles": "total_miles_tenths",
            "Tolls/Parking": "tolls_parking_cents",
            "Gas Purchases": "gas_purchase_cents",
            "Other Expenses": "other_expenses_cents",
            "Total Expenses": "total_expenses_cents",
            "Gross Business Income": "gross_business_income_cents",
            "Income After Logged Expenses": "income_after_logged_expenses_cents",
        }
        money_keys = {
            "tolls_parking_cents",
            "gas_purchase_cents",
            "other_expenses_cents",
            "total_expenses_cents",
            "gross_business_income_cents",
            "income_after_logged_expenses_cents",
        }

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["period_type", "summary_month", "metric", "value"])
            for period_type in ("month_to_date", "year_to_date"):
                period_data = summary["month" if period_type == "month_to_date" else "year"]
                for label in self.summary_keys:
                    key = label_to_key[label]
                    raw_value = period_data[key]
                    formatted = cents_to_str(raw_value) if key in money_keys else tenths_to_str(raw_value)
                    writer.writerow([period_type, month_filter, label, formatted])

        self.status_var.set(f"Exported summary to {path}.")
        messagebox.showinfo("Export Summary", f"Exported summary for {month_filter}.")



    def export_tax_estimate_csv(self) -> None:
        month_filter = self.export_tax_month_var.get().strip() or date.today().strftime("%Y-%m")
        try:
            tax_basis = self.db.get_tax_basis(month_filter)
        except ValueError:
            messagebox.showerror("Invalid Month", "Tax export month must be YYYY-MM.")
            return

        results = calculate_tax_estimate(tax_basis, self.tax_filing_status)
        path = filedialog.asksaveasfilename(
            title="Save Tax Estimate CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"tax_estimate_{month_filter}.csv",
        )
        if not path:
            return

        rows = [
            ("meta", "Tax Year", str(TAX_YEAR)),
            ("meta", "Filing Status", FILING_STATUS_LABELS[self.tax_filing_status]),
            ("meta", "Basis", "If the tax year ended today"),
            ("meta", "Scope", TAX_SCOPE_NOTE),
            ("meta", "Disclaimer", TAX_DISCLAIMER),
            ("federal", "Gross Business Income", cents_to_str(results["gross_business_income_cents"])),
            ("federal", "Mileage Deduction", cents_to_str(results["mileage_deduction_cents"])),
            ("federal", "Deductible Tolls/Parking", cents_to_str(results["deductible_tolls_parking_cents"])),
            ("federal", "Net Business Profit", cents_to_str(results["net_business_profit_cents"])),
            ("federal", "Net Earnings for SE Tax", cents_to_str(results["net_earnings_for_se_tax_cents"])),
            ("federal", "Estimated Self-Employment Tax", cents_to_str(results["estimated_self_employment_tax_cents"])),
            ("federal", "SE Tax Status", results["se_tax_status"]),
            ("federal", "Deductible Half of SE Tax", cents_to_str(results["deductible_half_se_tax_cents"])),
            ("federal", "Estimated Federal AGI", cents_to_str(results["estimated_federal_agi_cents"])),
            ("federal", "Standard Deduction", cents_to_str(results["standard_deduction_cents"])),
            ("federal", "Estimated Federal Taxable Income", cents_to_str(results["estimated_federal_taxable_income_cents"])),
            ("federal", "Estimated Federal Income Tax", cents_to_str(results["estimated_federal_income_tax_cents"])),
            ("federal", "Estimated Total Federal Tax", cents_to_str(results["estimated_total_federal_tax_cents"])),
            ("ohio", "Ohio Starting Income", cents_to_str(results["ohio_starting_income_cents"])),
            ("ohio", "Ohio Business Income Deduction", cents_to_str(results["ohio_business_income_deduction_cents"])),
            ("ohio", "Ohio Taxable Business Income", cents_to_str(results["ohio_taxable_business_income_cents"])),
            ("ohio", "Estimated Ohio State Tax", cents_to_str(results["estimated_ohio_state_tax_cents"])),
            ("ohio", "Ohio Status", results["ohio_status"]),
            ("ohio", "School District Tax", results["school_district_tax_status"]),
            ("combined", "Estimated Total Federal Tax", cents_to_str(results["estimated_total_federal_tax_cents"])),
            ("combined", "Estimated Ohio State Tax", cents_to_str(results["estimated_ohio_state_tax_cents"])),
            ("combined", "Combined Estimated Tax", cents_to_str(results["combined_estimated_tax_cents"])),
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["section", "metric", "value"])
            for row in rows:
                writer.writerow(row)

        self.status_var.set(f"Exported tax estimate to {path}.")
        messagebox.showinfo("Export Tax Estimate", f"Exported tax estimate for {month_filter}.")

    def create_backup(self) -> None:
        ensure_app_dirs()
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = BACKUP_DIR / f"flex_tracker_backup_{stamp}.db"
        shutil.copy2(DB_PATH, dest)
        self.status_var.set(f"Created backup at {dest}.")
        messagebox.showinfo("Backup Created", f"Backup saved to:\n{dest}")


if __name__ == "__main__":
    app = FlexTrackerApp()
    app.mainloop()
