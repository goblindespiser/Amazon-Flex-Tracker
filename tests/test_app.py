import unittest

from app import (
    calculate_progressive_tax_cents,
    calculate_qbi_deduction_cents,
    calculate_tax_estimate,
    month_range_for,
    parse_date,
    parse_non_negative_money_to_cents,
)
from states import get_available_states
from states.california import (
    _calculate_california_tax_from_table,
    _calculate_california_prop22_info,
    calculate_california_tax,
)
from states.florida import calculate_florida_tax
from states.illinois import calculate_illinois_tax
from states.new_york import calculate_new_york_tax
from states.new_york import _calculate_new_york_city_tax_table_cents
from states.north_carolina import calculate_north_carolina_tax
from states.ohio import calculate_ohio_tax
from states.pennsylvania import calculate_pennsylvania_tax
from states.texas import calculate_texas_tax
from states.virginia import calculate_virginia_tax


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

    def test_qbi_deduction_is_capped_by_taxable_income(self) -> None:
        self.assertEqual(
            calculate_qbi_deduction_cents(
                net_business_profit_cents=5_000_000,
                deductible_half_se_tax_cents=0,
                taxable_income_before_qbi_cents=1_000_000,
            ),
            200_000,
        )

    def test_tax_estimate_zero_business_activity(self) -> None:
        tax_basis = {
            "gross_business_income_cents": 0,
            "route_hours_tenths": 0,
            "business_miles_tenths": 0,
            "tolls_parking_cents": 0,
        }

        results = calculate_tax_estimate(tax_basis, "single", "ohio")

        self.assertEqual(results["estimated_self_employment_tax_cents"], 0)
        self.assertEqual(results["estimated_federal_income_tax_cents"], 0)
        self.assertEqual(results["estimated_state_tax_cents"], 0)
        self.assertEqual(results["combined_estimated_tax_cents"], 0)
        self.assertEqual(results["estimated_qbi_deduction_cents"], 0)

    def test_tax_estimate_positive_activity_produces_mileage_deduction(self) -> None:
        tax_basis = {
            "gross_business_income_cents": 500_000,
            "route_hours_tenths": 10,
            "business_miles_tenths": 1_000,
            "tolls_parking_cents": 2_500,
        }

        results = calculate_tax_estimate(tax_basis, "single", "ohio")

        self.assertEqual(results["mileage_deduction_cents"], 7250)
        self.assertEqual(results["net_business_profit_cents"], 490_250)
        self.assertGreaterEqual(results["combined_estimated_tax_cents"], 0)

    def test_tax_estimate_applies_qbi_deduction_to_federal_taxable_income(self) -> None:
        tax_basis = {
            "gross_business_income_cents": 5_000_000,
            "route_hours_tenths": 100,
            "business_miles_tenths": 0,
            "tolls_parking_cents": 0,
        }

        results = calculate_tax_estimate(tax_basis, "single", "ohio")

        self.assertGreater(results["estimated_federal_taxable_income_before_qbi_cents"], 0)
        self.assertGreater(results["estimated_qbi_deduction_cents"], 0)
        self.assertLess(
            results["estimated_federal_taxable_income_cents"],
            results["estimated_federal_taxable_income_before_qbi_cents"],
        )

    def test_ohio_tax_module_zero_agi_is_zero(self) -> None:
        results = calculate_ohio_tax({"net_business_profit_cents": 0}, "single")

        self.assertEqual(results["estimated_state_tax_cents"], 0)
        self.assertEqual(results["state_status"], "Below Ohio estimated quarterly payment threshold")

    def test_available_states_includes_ohio_and_california(self) -> None:
        available_states = get_available_states()

        self.assertEqual(available_states["ohio"], "Ohio")
        self.assertEqual(available_states["california"], "California")
        self.assertEqual(available_states["texas"], "Texas")
        self.assertEqual(available_states["florida"], "Florida")
        self.assertEqual(available_states["illinois"], "Illinois")
        self.assertEqual(available_states["virginia"], "Virginia")
        self.assertEqual(available_states["pennsylvania"], "Pennsylvania")
        self.assertEqual(available_states["north_carolina"], "North Carolina")
        self.assertEqual(available_states["new_york"], "New York")

    def test_california_tax_does_not_automatically_add_back_half_self_employment_tax(self) -> None:
        results = calculate_california_tax(
            {
                "estimated_federal_agi_cents": 1_000_000,
                "deductible_half_se_tax_cents": 10_000,
                "route_hours_tenths": 0,
                "business_miles_tenths": 0,
                "gross_business_income_cents": 0,
            },
            "single",
        )

        self.assertEqual(results["state_starting_income_cents"], 1_000_000)
        self.assertEqual(results["state_business_income_deduction_cents"], 0)
        self.assertGreaterEqual(results["estimated_state_tax_cents"], 0)
        self.assertIn("estimated quarterly payment threshold", results["state_status"])

    def test_california_prop22_info_uses_logged_hours_miles_and_pay(self) -> None:
        results = _calculate_california_prop22_info(
            {
                "route_hours_tenths": 20,
                "business_miles_tenths": 500,
                "gross_business_income_cents": 5_000,
            }
        )

        self.assertEqual(results["prop22_minimum_pay_rate_cents_per_hour"], 2028)
        self.assertEqual(results["prop22_mileage_rate_cents_per_mile"], 37)
        self.assertEqual(results["prop22_engaged_time_floor_cents"], 4056)
        self.assertEqual(results["prop22_mileage_floor_cents"], 1850)
        self.assertEqual(results["prop22_estimated_floor_cents"], 5906)
        self.assertEqual(results["prop22_estimated_difference_cents"], -906)
        self.assertEqual(results["prop22_estimated_payment_cents"], 906)

    def test_california_tax_table_matches_official_single_row(self) -> None:
        self.assertEqual(_calculate_california_tax_from_table(10_000_000, "single"), 573_600)

    def test_california_tax_table_matches_official_joint_row(self) -> None:
        self.assertEqual(
            _calculate_california_tax_from_table(10_000_000, "married_filing_jointly"),
            306_800,
        )

    def test_california_tax_table_matches_official_head_of_household_row(self) -> None:
        self.assertEqual(
            _calculate_california_tax_from_table(10_000_000, "head_of_household"),
            370_800,
        )

    def test_ohio_tax_uses_net_business_profit_not_federal_agi(self) -> None:
        results = calculate_ohio_tax(
            {
                "estimated_federal_agi_cents": 29_500_000,
                "net_business_profit_cents": 30_000_000,
            },
            "single",
        )

        self.assertEqual(results["state_starting_income_cents"], 30_000_000)
        self.assertEqual(results["state_taxable_business_income_cents"], 5_000_000)
        self.assertEqual(results["estimated_state_tax_cents"], 150_000)

    def test_texas_tax_is_zero(self) -> None:
        results = calculate_texas_tax(
            {
                "net_business_profit_cents": 123_456,
            },
            "single",
        )

        self.assertEqual(results["estimated_state_tax_cents"], 0)
        self.assertEqual(results["state_starting_income_cents"], 123_456)
        self.assertIn("no state individual income tax", results["state_status"])

    def test_florida_tax_is_zero(self) -> None:
        results = calculate_florida_tax(
            {
                "net_business_profit_cents": 654_321,
            },
            "single",
        )

        self.assertEqual(results["estimated_state_tax_cents"], 0)
        self.assertEqual(results["state_starting_income_cents"], 654_321)
        self.assertIn("no state individual income tax", results["state_status"])

    def test_illinois_tax_uses_flat_rate(self) -> None:
        results = calculate_illinois_tax(
            {
                "estimated_federal_agi_cents": 100_000,
            },
            "single",
        )

        self.assertEqual(results["estimated_state_tax_cents"], 4950)
        self.assertEqual(results["state_starting_income_cents"], 100_000)
        self.assertIn("estimated quarterly payment threshold", results["state_status"])
        self.assertIn("$950.50", results["state_status"])

    def test_virginia_tax_uses_standard_deduction_and_exemption(self) -> None:
        results = calculate_virginia_tax(
            {
                "estimated_federal_agi_cents": 1_000_000,
            },
            "single",
        )

        self.assertEqual(results["state_starting_income_cents"], 1_000_000)
        self.assertEqual(results["state_business_income_deduction_cents"], 968_000)
        self.assertEqual(results["state_taxable_business_income_cents"], 32_000)
        self.assertEqual(results["estimated_state_tax_cents"], 640)
        self.assertIn("estimated quarterly payment threshold", results["state_status"])

    def test_pennsylvania_tax_uses_flat_rate_on_net_profits(self) -> None:
        results = calculate_pennsylvania_tax(
            {
                "net_business_profit_cents": 100_000,
                "estimated_federal_agi_cents": 50_000,
            },
            "single",
        )

        self.assertEqual(results["state_starting_income_cents"], 100_000)
        self.assertEqual(results["state_taxable_business_income_cents"], 100_000)
        self.assertEqual(results["estimated_state_tax_cents"], 3070)
        self.assertIn("estimated quarterly payment threshold", results["state_status"])

    def test_north_carolina_tax_uses_standard_deduction_then_flat_rate(self) -> None:
        results = calculate_north_carolina_tax(
            {
                "estimated_federal_agi_cents": 2_000_000,
            },
            "single",
        )

        self.assertEqual(results["state_starting_income_cents"], 2_000_000)
        self.assertEqual(results["state_business_income_deduction_cents"], 1_275_000)
        self.assertEqual(results["state_taxable_business_income_cents"], 725_000)
        self.assertEqual(results["estimated_state_tax_cents"], 28_928)
        self.assertIn("estimated quarterly payment threshold", results["state_status"])

    def test_new_york_tax_uses_standard_deduction_then_official_table(self) -> None:
        results = calculate_new_york_tax(
            {
                "estimated_federal_agi_cents": 2_000_000,
            },
            "single",
        )

        self.assertEqual(results["state_starting_income_cents"], 2_000_000)
        self.assertEqual(results["state_business_income_deduction_cents"], 800_000)
        self.assertEqual(results["state_taxable_business_income_cents"], 1_200_000)
        self.assertEqual(results["estimated_state_tax_cents"], 50_100)
        self.assertIn("estimated quarterly payment threshold", results["state_status"])

    def test_new_york_tax_uses_official_tax_table_for_lower_income(self) -> None:
        results = calculate_new_york_tax(
            {
                "estimated_federal_agi_cents": 2_000_000,
            },
            "married_filing_jointly",
        )

        self.assertEqual(results["state_taxable_business_income_cents"], 395_000)
        self.assertEqual(results["estimated_state_tax_cents"], 15_900)

    def test_new_york_tax_uses_high_agi_computation_when_required(self) -> None:
        results = calculate_new_york_tax(
            {
                "estimated_federal_agi_cents": 12_000_000,
            },
            "single",
        )

        self.assertEqual(results["state_taxable_business_income_cents"], 11_200_000)
        self.assertEqual(results["estimated_state_tax_cents"], 629_200)

    def test_new_york_tax_can_include_nyc_resident_tax(self) -> None:
        results = calculate_new_york_tax(
            {
                "estimated_federal_agi_cents": 2_000_000,
                "tax_locality": "nyc_resident",
            },
            "single",
        )

        self.assertEqual(results["state_taxable_business_income_cents"], 1_200_000)
        self.assertEqual(results["estimated_state_tax_cents"], 50_100)
        self.assertEqual(results["local_starting_income_cents"], 1_200_000)
        self.assertEqual(results["estimated_local_tax_cents"], 37_000)
        self.assertEqual(results["school_district_tax_status"], "NYC resident estimate included")
        self.assertIn("threshold exceeded by $571.00", results["state_status"])

    def test_new_york_city_tax_table_matches_official_single_row(self) -> None:
        self.assertEqual(_calculate_new_york_city_tax_table_cents(3_000_000, "single"), 105_000)

    def test_new_york_city_tax_table_matches_official_joint_example_row(self) -> None:
        self.assertEqual(_calculate_new_york_city_tax_table_cents(3_827_500, "married_filing_jointly"), 129_200)

    def test_new_york_tax_can_include_yonkers_resident_surcharge(self) -> None:
        results = calculate_new_york_tax(
            {
                "estimated_federal_agi_cents": 2_000_000,
                "tax_locality": "yonkers_resident",
            },
            "single",
        )

        self.assertEqual(results["estimated_state_tax_cents"], 50_100)
        self.assertEqual(results["local_starting_income_cents"], 50_100)
        self.assertEqual(results["estimated_local_tax_cents"], 8_400)
        self.assertEqual(results["school_district_tax_status"], "Yonkers resident estimate included")
        self.assertIn("threshold exceeded by $285.00", results["state_status"])


if __name__ == "__main__":
    unittest.main()
