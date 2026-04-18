import unittest

from app import (
    calculate_progressive_tax_cents,
    calculate_tax_estimate,
    month_range_for,
    parse_date,
    parse_non_negative_money_to_cents,
)


class TestHelpers(unittest.TestCase):
    def test_month_range_for_april(self) -> None:
        self.assertEqual(month_range_for("2026-04"), ("2026-04-01", "2026-05-01"))

    def test_parse_date_accepts_iso_date(self) -> None:
        self.assertEqual(parse_date("2026-04-18", "Log Date"), "2026-04-18")

    def test_parse_date_rejects_invalid_format(self) -> None:
        with self.assertRaises(ValueError):
            parse_date("04/18/2026", "Log Date")

    def test_parse_money_rounds_to_cents(self) -> None:
        self.assertEqual(parse_non_negative_money_to_cents("12.345", "Amount"), 1235)

    def test_parse_money_rejects_negative_values(self) -> None:
        with self.assertRaises(ValueError):
            parse_non_negative_money_to_cents("-1.00", "Amount")


class TestTaxMath(unittest.TestCase):
    def test_progressive_tax_zero_income_is_zero(self) -> None:
        self.assertEqual(calculate_progressive_tax_cents(0, "single"), 0)

    def test_progressive_tax_single_first_bracket(self) -> None:
        self.assertEqual(calculate_progressive_tax_cents(1_000_000, "single"), 100_000)

    def test_tax_estimate_zero_business_activity(self) -> None:
        tax_basis = {
            "gross_business_income_cents": 0,
            "business_miles_tenths": 0,
            "tolls_parking_cents": 0,
        }

        results = calculate_tax_estimate(tax_basis, "single")

        self.assertEqual(results["estimated_self_employment_tax_cents"], 0)
        self.assertEqual(results["estimated_federal_income_tax_cents"], 0)
        self.assertEqual(results["estimated_ohio_state_tax_cents"], 0)
        self.assertEqual(results["combined_estimated_tax_cents"], 0)

    def test_tax_estimate_positive_activity_produces_mileage_deduction(self) -> None:
        tax_basis = {
            "gross_business_income_cents": 500_000,
            "business_miles_tenths": 1_000,
            "tolls_parking_cents": 2_500,
        }

        results = calculate_tax_estimate(tax_basis, "single")

        self.assertEqual(results["mileage_deduction_cents"], 7250)
        self.assertEqual(results["net_business_profit_cents"], 490_250)
        self.assertGreaterEqual(results["combined_estimated_tax_cents"], 0)


if __name__ == "__main__":
    unittest.main()
