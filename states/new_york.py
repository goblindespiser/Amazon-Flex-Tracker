from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

STATE_CODE = "new_york"
STATE_NAME = "New York"
STATE_TAX_FRAME_TITLE = "New York Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated New York State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "New York AGI",
    "state_business_income_deduction_cents": "New York Standard Deduction",
    "state_taxable_business_income_cents": "New York Taxable Income",
    "estimated_state_tax_cents": "Estimated New York State Tax",
    "state_status": "New York Status",
    "school_district_tax_status": "New York City / Yonkers Tax",
    "state_soft_disclaimer": "New York Note",
}
LOCALITY_OPTIONS = {
    "": "None",
    "nyc_resident": "NYC resident",
    "yonkers_resident": "Yonkers resident",
}
NEW_YORK_CITY_FRAME_TITLE = "New York City Tax (Local)"
NEW_YORK_CITY_ESTIMATED_TAX_LABEL = "Estimated New York City Resident Tax"
NEW_YORK_CITY_FIELD_LABELS = {
    "local_starting_income_cents": "New York City Taxable Income",
    "estimated_local_tax_cents": "Estimated New York City Resident Tax",
    "local_status": "New York City Scope",
    "local_soft_disclaimer": "New York City Note",
}
YONKERS_FRAME_TITLE = "Yonkers Tax (Local)"
YONKERS_ESTIMATED_TAX_LABEL = "Estimated Yonkers Resident Surcharge"
YONKERS_FIELD_LABELS = {
    "local_starting_income_cents": "Yonkers Surcharge Base",
    "estimated_local_tax_cents": "Estimated Yonkers Resident Surcharge",
    "local_status": "Yonkers Scope",
    "local_soft_disclaimer": "Yonkers Note",
}

NEW_YORK_STANDARD_DEDUCTION_CENTS = {
    "single": 800_000,
    "married_filing_jointly": 1_605_000,
    "married_filing_separately": 800_000,
    "head_of_household": 1_120_000,
    "qualifying_surviving_spouse": 1_605_000,
}

NEW_YORK_ESTIMATED_PAYMENT_THRESHOLD_CENTS = 30_000
YONKERS_RESIDENT_SURCHARGE_RATE = Decimal("0.1675")
NEW_YORK_CITY_TAX_BRACKETS_CENTS = {
    "single": [
        (1_200_000, Decimal("0.03078")),
        (2_500_000, Decimal("0.03762")),
        (5_000_000, Decimal("0.03819")),
        (None, Decimal("0.03876")),
    ],
    "married_filing_separately": [
        (1_200_000, Decimal("0.03078")),
        (2_500_000, Decimal("0.03762")),
        (5_000_000, Decimal("0.03819")),
        (None, Decimal("0.03876")),
    ],
    "married_filing_jointly": [
        (2_160_000, Decimal("0.03078")),
        (4_500_000, Decimal("0.03762")),
        (9_000_000, Decimal("0.03819")),
        (None, Decimal("0.03876")),
    ],
    "qualifying_surviving_spouse": [
        (2_160_000, Decimal("0.03078")),
        (4_500_000, Decimal("0.03762")),
        (9_000_000, Decimal("0.03819")),
        (None, Decimal("0.03876")),
    ],
    "head_of_household": [
        (1_440_000, Decimal("0.03078")),
        (3_000_000, Decimal("0.03762")),
        (6_000_000, Decimal("0.03819")),
        (None, Decimal("0.03876")),
    ],
}
NEW_YORK_CITY_TAX_TABLE_SCHEDULES = {
    "single": [
        (0, 1_200_000, 0, Decimal("0.03078"), 0),
        (1_200_000, 2_500_000, 36_900, Decimal("0.03762"), 1_200_000),
        (2_500_000, 5_000_000, 85_800, Decimal("0.03819"), 2_500_000),
        (5_000_000, None, 181_300, Decimal("0.03876"), 5_000_000),
    ],
    "married_filing_separately": [
        (0, 1_200_000, 0, Decimal("0.03078"), 0),
        (1_200_000, 2_500_000, 36_900, Decimal("0.03762"), 1_200_000),
        (2_500_000, 5_000_000, 85_800, Decimal("0.03819"), 2_500_000),
        (5_000_000, None, 181_300, Decimal("0.03876"), 5_000_000),
    ],
    "married_filing_jointly": [
        (0, 2_160_000, 0, Decimal("0.03078"), 0),
        (2_160_000, 4_500_000, 66_500, Decimal("0.03762"), 2_160_000),
        (4_500_000, 9_000_000, 154_500, Decimal("0.03819"), 4_500_000),
        (9_000_000, None, 326_400, Decimal("0.03876"), 9_000_000),
    ],
    "qualifying_surviving_spouse": [
        (0, 2_160_000, 0, Decimal("0.03078"), 0),
        (2_160_000, 4_500_000, 66_500, Decimal("0.03762"), 2_160_000),
        (4_500_000, 9_000_000, 154_500, Decimal("0.03819"), 4_500_000),
        (9_000_000, None, 326_400, Decimal("0.03876"), 9_000_000),
    ],
    "head_of_household": [
        (0, 1_440_000, 0, Decimal("0.03078"), 0),
        (1_440_000, 3_000_000, 44_300, Decimal("0.03762"), 1_440_000),
        (3_000_000, 6_000_000, 103_000, Decimal("0.03819"), 3_000_000),
        (6_000_000, None, 217_600, Decimal("0.03876"), 6_000_000),
    ],
}
NEW_YORK_TAX_BRACKETS_CENTS = {
    "single": [
        (850_000, Decimal("0.04")),
        (1_170_000, Decimal("0.045")),
        (1_390_000, Decimal("0.0525")),
        (8_065_000, Decimal("0.055")),
        (21_540_000, Decimal("0.06")),
        (107_755_000, Decimal("0.0685")),
        (500_000_000, Decimal("0.0965")),
        (2_500_000_000, Decimal("0.103")),
        (None, Decimal("0.109")),
    ],
    "married_filing_separately": [
        (850_000, Decimal("0.04")),
        (1_170_000, Decimal("0.045")),
        (1_390_000, Decimal("0.0525")),
        (8_065_000, Decimal("0.055")),
        (21_540_000, Decimal("0.06")),
        (107_755_000, Decimal("0.0685")),
        (500_000_000, Decimal("0.0965")),
        (2_500_000_000, Decimal("0.103")),
        (None, Decimal("0.109")),
    ],
    "married_filing_jointly": [
        (1_715_000, Decimal("0.04")),
        (2_360_000, Decimal("0.045")),
        (2_790_000, Decimal("0.0525")),
        (16_155_000, Decimal("0.055")),
        (32_320_000, Decimal("0.06")),
        (215_535_000, Decimal("0.0685")),
        (500_000_000, Decimal("0.0965")),
        (2_500_000_000, Decimal("0.103")),
        (None, Decimal("0.109")),
    ],
    "qualifying_surviving_spouse": [
        (1_715_000, Decimal("0.04")),
        (2_360_000, Decimal("0.045")),
        (2_790_000, Decimal("0.0525")),
        (16_155_000, Decimal("0.055")),
        (32_320_000, Decimal("0.06")),
        (215_535_000, Decimal("0.0685")),
        (500_000_000, Decimal("0.0965")),
        (2_500_000_000, Decimal("0.103")),
        (None, Decimal("0.109")),
    ],
    "head_of_household": [
        (1_280_000, Decimal("0.04")),
        (1_765_000, Decimal("0.045")),
        (2_090_000, Decimal("0.0525")),
        (10_765_000, Decimal("0.055")),
        (26_930_000, Decimal("0.06")),
        (161_645_000, Decimal("0.0685")),
        (500_000_000, Decimal("0.0965")),
        (2_500_000_000, Decimal("0.103")),
        (None, Decimal("0.109")),
    ],
}


def _money_to_cents(value: Decimal) -> int:
    return int((value * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _round_cents_to_whole_dollar_cents(value_cents: int) -> int:
    rounded_dollars = (Decimal(value_cents) / Decimal("100")).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )
    return int(rounded_dollars) * 100


def _calculate_progressive_new_york_tax_cents(taxable_income_cents: int, filing_status: str) -> int:
    taxable_income_cents = max(taxable_income_cents, 0)
    brackets = NEW_YORK_TAX_BRACKETS_CENTS[filing_status]
    previous_cap = 0
    total = Decimal("0")

    for cap, rate in brackets:
        current_cap = taxable_income_cents if cap is None else min(taxable_income_cents, cap)
        if current_cap > previous_cap:
            bracket_amount = Decimal(current_cap - previous_cap) / Decimal("100")
            total += bracket_amount * rate
        previous_cap = current_cap
        if current_cap >= taxable_income_cents:
            break

    return _money_to_cents(total)


def _calculate_progressive_new_york_city_tax_cents(taxable_income_cents: int, filing_status: str) -> int:
    taxable_income_cents = max(taxable_income_cents, 0)
    brackets = NEW_YORK_CITY_TAX_BRACKETS_CENTS[filing_status]
    previous_cap = 0
    total = Decimal("0")

    for cap, rate in brackets:
        current_cap = taxable_income_cents if cap is None else min(taxable_income_cents, cap)
        if current_cap > previous_cap:
            bracket_amount = Decimal(current_cap - previous_cap) / Decimal("100")
            total += bracket_amount * rate
        previous_cap = current_cap
        if current_cap >= taxable_income_cents:
            break

    return _money_to_cents(total)


def _calculate_new_york_tax_table_cents(taxable_income_cents: int, filing_status: str) -> int:
    taxable_income_cents = _round_cents_to_whole_dollar_cents(max(taxable_income_cents, 0))
    taxable_income_dollars = Decimal(taxable_income_cents) / Decimal("100")

    if taxable_income_dollars < 13:
        lower = Decimal("0")
        upper = Decimal("13")
    elif taxable_income_dollars < 25:
        lower = Decimal("13")
        upper = Decimal("25")
    elif taxable_income_dollars < 50:
        lower = Decimal("25")
        upper = Decimal("50")
    elif taxable_income_dollars < 100:
        lower = Decimal("50")
        upper = Decimal("100")
    else:
        lower = (taxable_income_dollars // Decimal("50")) * Decimal("50")
        upper = lower + Decimal("50")

    midpoint_cents = _money_to_cents((lower + upper) / Decimal("2"))
    midpoint_tax_cents = _calculate_progressive_new_york_tax_cents(midpoint_cents, filing_status)
    midpoint_tax_dollars = (Decimal(midpoint_tax_cents) / Decimal("100")).quantize(
        Decimal("1"),
        rounding=ROUND_HALF_UP,
    )
    return int(midpoint_tax_dollars) * 100


def _calculate_new_york_city_tax_table_cents(taxable_income_cents: int, filing_status: str) -> int:
    taxable_income_cents = _round_cents_to_whole_dollar_cents(max(taxable_income_cents, 0))
    taxable_income_dollars = Decimal(taxable_income_cents) / Decimal("100")

    if taxable_income_dollars < 18:
        lower = Decimal("0")
        upper = Decimal("18")
    elif taxable_income_dollars < 25:
        lower = Decimal("18")
        upper = Decimal("25")
    elif taxable_income_dollars < 50:
        lower = Decimal("25")
        upper = Decimal("50")
    elif taxable_income_dollars < 100:
        lower = Decimal("50")
        upper = Decimal("100")
    else:
        lower = (taxable_income_dollars // Decimal("50")) * Decimal("50")
        upper = lower + Decimal("50")

    midpoint_cents = _money_to_cents((lower + upper) / Decimal("2"))
    for lower_bound_cents, upper_bound_cents, base_tax_cents, rate, rate_start_cents in NEW_YORK_CITY_TAX_TABLE_SCHEDULES[filing_status]:
        if upper_bound_cents is None or midpoint_cents < upper_bound_cents:
            midpoint_tax_dollars = (
                Decimal(base_tax_cents) / Decimal("100")
                + (Decimal(midpoint_cents - rate_start_cents) / Decimal("100")) * rate
            ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
            return int(midpoint_tax_dollars) * 100

    return 0


def _calculate_new_york_high_agi_tax_cents(
    new_york_agi_cents: int,
    new_york_taxable_income_cents: int,
    filing_status: str,
) -> int:
    if new_york_agi_cents > 2_500_000_000:
        return _money_to_cents((Decimal(new_york_taxable_income_cents) / Decimal("100")) * Decimal("0.109"))

    schedule_tax_cents = _calculate_progressive_new_york_tax_cents(new_york_taxable_income_cents, filing_status)
    agi_excess_ratio = (
        (Decimal(max(new_york_agi_cents - 10_765_000, 0)) / Decimal("100"))
        / Decimal("50000")
    ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    first_phase_configs = {
        "married_filing_jointly": (16_155_000, Decimal("0.055"), 15_765_000),
        "qualifying_surviving_spouse": (16_155_000, Decimal("0.055"), 15_765_000),
        "single": (21_540_000, Decimal("0.06"), 15_765_000),
        "married_filing_separately": (21_540_000, Decimal("0.06"), 15_765_000),
        "head_of_household": (26_930_000, Decimal("0.06"), 15_765_000),
    }
    first_phase_limit_cents, top_rate, full_rate_agi_cents = first_phase_configs[filing_status]
    if new_york_taxable_income_cents <= first_phase_limit_cents:
        top_rate_tax_cents = _money_to_cents((Decimal(new_york_taxable_income_cents) / Decimal("100")) * top_rate)
        if new_york_agi_cents >= full_rate_agi_cents:
            return top_rate_tax_cents
        benefit_cents = top_rate_tax_cents - schedule_tax_cents
        return schedule_tax_cents + _money_to_cents((Decimal(benefit_cents) / Decimal("100")) * agi_excess_ratio)

    recapture_configs = {
        "married_filing_jointly": [
            (16_155_000, 32_320_000, 33_300, 80_700),
            (32_320_000, 215_535_000, 114_000, 274_700),
            (215_535_000, 500_000_000, 388_700, 6_035_000),
            (500_000_000, 2_500_000_000, 6_423_700, 3_250_000),
        ],
        "qualifying_surviving_spouse": [
            (16_155_000, 32_320_000, 33_300, 80_700),
            (32_320_000, 215_535_000, 114_000, 274_700),
            (215_535_000, 500_000_000, 388_700, 6_035_000),
            (500_000_000, 2_500_000_000, 6_423_700, 3_250_000),
        ],
        "single": [
            (21_540_000, 107_755_000, 56_800, 183_100),
            (107_755_000, 500_000_000, 239_900, 3_017_200),
            (500_000_000, 2_500_000_000, 3_257_100, 3_250_000),
        ],
        "married_filing_separately": [
            (21_540_000, 107_755_000, 56_800, 183_100),
            (107_755_000, 500_000_000, 239_900, 3_017_200),
            (500_000_000, 2_500_000_000, 3_257_100, 3_250_000),
        ],
        "head_of_household": [
            (26_930_000, 161_645_000, 78_700, 228_900),
            (161_645_000, 500_000_000, 307_600, 4_526_100),
            (500_000_000, 2_500_000_000, 4_833_700, 3_250_000),
        ],
    }

    for lower_bound_cents, upper_bound_cents, recapture_base_cents, incremental_benefit_cents in recapture_configs[filing_status]:
        if lower_bound_cents < new_york_taxable_income_cents <= upper_bound_cents:
            ratio = (
                (Decimal(min(max(new_york_agi_cents - lower_bound_cents, 0), 5_000_000)) / Decimal("100"))
                / Decimal("50000")
            ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            incremental_amount_cents = _money_to_cents(
                (Decimal(incremental_benefit_cents) / Decimal("100")) * ratio
            )
            return schedule_tax_cents + recapture_base_cents + incremental_amount_cents

    return schedule_tax_cents


def calculate_new_york_tax(state_inputs: dict, filing_status: str) -> dict:
    selected_locality = state_inputs.get("tax_locality", "")
    new_york_agi_cents = _round_cents_to_whole_dollar_cents(max(state_inputs["estimated_federal_agi_cents"], 0))
    new_york_standard_deduction_cents = NEW_YORK_STANDARD_DEDUCTION_CENTS[filing_status]
    new_york_taxable_income_cents = max(new_york_agi_cents - new_york_standard_deduction_cents, 0)
    if new_york_agi_cents <= 10_765_000 and new_york_taxable_income_cents < 6_500_000:
        estimated_new_york_state_tax_cents = _calculate_new_york_tax_table_cents(
            new_york_taxable_income_cents,
            filing_status,
        )
    elif new_york_agi_cents > 10_765_000:
        estimated_new_york_state_tax_cents = _calculate_new_york_high_agi_tax_cents(
            new_york_agi_cents,
            new_york_taxable_income_cents,
            filing_status,
        )
    else:
        estimated_new_york_state_tax_cents = _calculate_progressive_new_york_tax_cents(
            new_york_taxable_income_cents,
            filing_status,
        )
    estimated_new_york_state_tax_cents = _round_cents_to_whole_dollar_cents(
        estimated_new_york_state_tax_cents
    )

    estimated_new_york_city_tax_cents = 0
    local_results: dict[str, int | str | dict] = {}
    if selected_locality == "nyc_resident":
        new_york_city_taxable_income_cents = new_york_taxable_income_cents
        if new_york_city_taxable_income_cents < 6_500_000:
            estimated_new_york_city_tax_cents = _calculate_new_york_city_tax_table_cents(
                new_york_city_taxable_income_cents,
                filing_status,
            )
        else:
            estimated_new_york_city_tax_cents = _calculate_progressive_new_york_city_tax_cents(
                new_york_city_taxable_income_cents,
                filing_status,
            )
        estimated_new_york_city_tax_cents = _round_cents_to_whole_dollar_cents(
            estimated_new_york_city_tax_cents
        )
        local_results = {
            "local_frame_title": NEW_YORK_CITY_FRAME_TITLE,
            "local_field_labels": NEW_YORK_CITY_FIELD_LABELS,
            "local_estimate_label": NEW_YORK_CITY_ESTIMATED_TAX_LABEL,
            "local_starting_income_cents": new_york_city_taxable_income_cents,
            "estimated_local_tax_cents": estimated_new_york_city_tax_cents,
            "local_status": "NYC resident; full-year estimate only",
            "local_soft_disclaimer": (
                "Full-year NYC resident estimate only. Household credit, school tax credit, mixed-residency "
                "joint returns, and part-year residency are not included."
            ),
        }
    elif selected_locality == "yonkers_resident":
        yonkers_surcharge_base_cents = estimated_new_york_state_tax_cents
        estimated_new_york_city_tax_cents = _round_cents_to_whole_dollar_cents(
            _money_to_cents(
                (Decimal(yonkers_surcharge_base_cents) / Decimal("100")) * YONKERS_RESIDENT_SURCHARGE_RATE
            )
        )
        local_results = {
            "local_frame_title": YONKERS_FRAME_TITLE,
            "local_field_labels": YONKERS_FIELD_LABELS,
            "local_estimate_label": YONKERS_ESTIMATED_TAX_LABEL,
            "local_starting_income_cents": yonkers_surcharge_base_cents,
            "estimated_local_tax_cents": estimated_new_york_city_tax_cents,
            "local_status": "Yonkers resident; full-year estimate only",
            "local_soft_disclaimer": (
                "Full-year Yonkers resident estimate only. Credits, other New York taxes, mixed-residency "
                "joint returns, and part-year residency are not included."
            ),
        }

    threshold_gap_cents = NEW_YORK_ESTIMATED_PAYMENT_THRESHOLD_CENTS - (
        estimated_new_york_state_tax_cents + estimated_new_york_city_tax_cents
    )
    if threshold_gap_cents >= 0:
        threshold_gap_dollars = Decimal(threshold_gap_cents) / Decimal("100")
        new_york_status = (
            "Below New York estimated quarterly payment threshold by "
            f"${threshold_gap_dollars:.2f}; simplified resident estimate"
        )
    else:
        threshold_over_dollars = Decimal(-threshold_gap_cents) / Decimal("100")
        new_york_status = (
            "New York estimated quarterly payment threshold exceeded by "
            f"${threshold_over_dollars:.2f}; simplified resident estimate"
        )

    return {
        "state_starting_income_cents": new_york_agi_cents,
        "state_business_income_deduction_cents": new_york_standard_deduction_cents,
        "state_taxable_business_income_cents": new_york_taxable_income_cents,
        "estimated_state_tax_cents": estimated_new_york_state_tax_cents,
        "state_status": new_york_status,
        "school_district_tax_status": (
            "NYC resident estimate included"
            if selected_locality == "nyc_resident"
            else "Yonkers resident estimate included"
            if selected_locality == "yonkers_resident"
            else "No New York City or Yonkers tax included"
        ),
        "state_soft_disclaimer": (
            "Uses the latest published New York resident tax table and worksheets currently available. "
            "A full 2026 resident instruction set is not yet published."
        ),
        **local_results,
    }
