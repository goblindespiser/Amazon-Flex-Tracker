from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

STATE_CODE = "california"
STATE_NAME = "California"
STATE_TAX_FRAME_TITLE = "California Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated California State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "California AGI",
    "state_business_income_deduction_cents": "California Adjustments",
    "state_taxable_business_income_cents": "California Taxable Income",
    "estimated_state_tax_cents": "Estimated California State Tax",
    "state_status": "California Status",
    "school_district_tax_status": "Behavioral Health Services Tax",
}

# California's 2026 estimated-tax worksheet instructs taxpayers to use the 2025
# Form 540/540NR tax tables and exemption credit amounts.
CALIFORNIA_STANDARD_DEDUCTION_CENTS = {
    "single": 570_600,
    "married_filing_jointly": 1_141_200,
    "married_filing_separately": 570_600,
    "head_of_household": 1_141_200,
    "qualifying_surviving_spouse": 1_141_200,
}

CALIFORNIA_PERSONAL_EXEMPTION_COUNT = {
    "single": 1,
    "married_filing_jointly": 2,
    "married_filing_separately": 1,
    "head_of_household": 1,
    "qualifying_surviving_spouse": 2,
}

CALIFORNIA_PERSONAL_EXEMPTION_CREDIT_CENTS = 15_300

CALIFORNIA_EXEMPTION_AGI_LIMITS_CENTS = {
    "single": 25_220_300,
    "married_filing_jointly": 50_441_100,
    "married_filing_separately": 25_220_300,
    "head_of_household": 37_831_000,
    "qualifying_surviving_spouse": 50_441_100,
}

CALIFORNIA_ESTIMATED_PAYMENT_THRESHOLD_CENTS = {
    "single": 50_000,
    "married_filing_jointly": 50_000,
    "married_filing_separately": 25_000,
    "head_of_household": 50_000,
    "qualifying_surviving_spouse": 50_000,
}

CALIFORNIA_TAX_SCHEDULES = {
    "single": [
        (1_107_900, Decimal("0.01"), 0),
        (2_626_400, Decimal("0.02"), 11_079),
        (4_145_200, Decimal("0.04"), 41_449),
        (5_754_200, Decimal("0.06"), 102_201),
        (7_272_400, Decimal("0.08"), 198_741),
        (37_147_900, Decimal("0.093"), 320_197),
        (44_577_100, Decimal("0.103"), 3_098_619),
        (74_295_300, Decimal("0.113"), 3_863_827),
        (None, Decimal("0.123"), 7_221_984),
    ],
    "married_filing_jointly": [
        (2_215_800, Decimal("0.01"), 0),
        (5_252_800, Decimal("0.02"), 22_158),
        (8_290_400, Decimal("0.04"), 82_898),
        (11_508_400, Decimal("0.06"), 204_402),
        (14_544_800, Decimal("0.08"), 397_482),
        (74_295_800, Decimal("0.093"), 640_394),
        (89_154_200, Decimal("0.103"), 6_197_237),
        (148_590_600, Decimal("0.113"), 7_727_652),
        (None, Decimal("0.123"), 14_443_965),
    ],
    "married_filing_separately": [
        (1_107_900, Decimal("0.01"), 0),
        (2_626_400, Decimal("0.02"), 11_079),
        (4_145_200, Decimal("0.04"), 41_449),
        (5_754_200, Decimal("0.06"), 102_201),
        (7_272_400, Decimal("0.08"), 198_741),
        (37_147_900, Decimal("0.093"), 320_197),
        (44_577_100, Decimal("0.103"), 3_098_619),
        (74_295_300, Decimal("0.113"), 3_863_827),
        (None, Decimal("0.123"), 7_221_984),
    ],
    "head_of_household": [
        (2_217_300, Decimal("0.01"), 0),
        (5_253_000, Decimal("0.02"), 22_173),
        (6_771_600, Decimal("0.04"), 82_887),
        (8_380_500, Decimal("0.06"), 143_631),
        (9_899_000, Decimal("0.08"), 240_165),
        (50_520_800, Decimal("0.093"), 361_645),
        (60_625_100, Decimal("0.103"), 4_139_472),
        (101_041_700, Decimal("0.113"), 5_180_215),
        (None, Decimal("0.123"), 9_747_291),
    ],
    "qualifying_surviving_spouse": [
        (2_215_800, Decimal("0.01"), 0),
        (5_252_800, Decimal("0.02"), 22_158),
        (8_290_400, Decimal("0.04"), 82_898),
        (11_508_400, Decimal("0.06"), 204_402),
        (14_544_800, Decimal("0.08"), 397_482),
        (74_295_800, Decimal("0.093"), 640_394),
        (89_154_200, Decimal("0.103"), 6_197_237),
        (148_590_600, Decimal("0.113"), 7_727_652),
        (None, Decimal("0.123"), 14_443_965),
    ],
}

CALIFORNIA_BHST_THRESHOLD_CENTS = 100_000_000
CALIFORNIA_BHST_RATE = Decimal("0.01")
CALIFORNIA_PROP22_PER_MILE_RATE = Decimal("0.37")
CALIFORNIA_PROP22_MINIMUM_WAGE = Decimal("16.90")
CALIFORNIA_PROP22_ENGAGED_RATE_MULTIPLIER = Decimal("1.20")


def _money_to_cents(amount_dollars: Decimal) -> int:
    return int((amount_dollars * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _round_cents_to_whole_dollars_cents(amount_cents: int) -> int:
    amount_dollars = Decimal(amount_cents) / Decimal("100")
    rounded_dollars = amount_dollars.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(rounded_dollars * Decimal("100"))


def _taxable_income_row_midpoint_cents(taxable_income_cents: int) -> int:
    taxable_income_dollars = int(
        (Decimal(taxable_income_cents) / Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    if taxable_income_dollars <= 0:
        return 0
    if taxable_income_dollars <= 50:
        return 2_550
    if taxable_income_dollars > 99_950:
        return 9_997_550

    row_start_dollars = 51 + ((taxable_income_dollars - 51) // 100) * 100
    return row_start_dollars * 100 + 4_950


def _calculate_california_tax_from_schedule(taxable_income_cents: int, filing_status: str) -> int:
    taxable_income_cents = max(taxable_income_cents, 0)
    schedules = CALIFORNIA_TAX_SCHEDULES[filing_status]
    lower_bound_cents = 0

    for upper_bound_cents, rate, base_tax_cents in schedules:
        if upper_bound_cents is None or taxable_income_cents <= upper_bound_cents:
            taxable_over_base_dollars = Decimal(taxable_income_cents - lower_bound_cents) / Decimal("100")
            tax_dollars = (Decimal(base_tax_cents) / Decimal("100")) + (taxable_over_base_dollars * rate)
            return _money_to_cents(tax_dollars)
        lower_bound_cents = upper_bound_cents

    return 0


def _calculate_california_tax_from_table(taxable_income_cents: int, filing_status: str) -> int:
    midpoint_cents = _taxable_income_row_midpoint_cents(taxable_income_cents)
    schedule_tax_cents = _calculate_california_tax_from_schedule(midpoint_cents, filing_status)
    return _round_cents_to_whole_dollars_cents(schedule_tax_cents)


def _calculate_personal_exemption_credit(estimated_california_agi_cents: int, filing_status: str) -> int:
    full_credit_cents = CALIFORNIA_PERSONAL_EXEMPTION_COUNT[filing_status] * CALIFORNIA_PERSONAL_EXEMPTION_CREDIT_CENTS
    agi_limit_cents = CALIFORNIA_EXEMPTION_AGI_LIMITS_CENTS[filing_status]

    if estimated_california_agi_cents <= agi_limit_cents:
        return full_credit_cents

    divisor = 125_000 if filing_status == "married_filing_separately" else 250_000
    reduction_units = (estimated_california_agi_cents - agi_limit_cents + divisor - 1) // divisor
    reduced_credit_cents = full_credit_cents - (reduction_units * 600 * CALIFORNIA_PERSONAL_EXEMPTION_COUNT[filing_status])
    return max(reduced_credit_cents, 0)


def _calculate_california_prop22_info(state_inputs: dict) -> dict:
    route_hours_tenths = state_inputs["route_hours_tenths"]
    business_miles_tenths = state_inputs["business_miles_tenths"]
    actual_pay_cents = state_inputs["gross_business_income_cents"]

    engaged_rate_cents_per_hour = _money_to_cents(
        CALIFORNIA_PROP22_MINIMUM_WAGE * CALIFORNIA_PROP22_ENGAGED_RATE_MULTIPLIER
    )
    mileage_rate_cents_per_mile = _money_to_cents(CALIFORNIA_PROP22_PER_MILE_RATE)

    engaged_time_floor_cents = _money_to_cents(
        (Decimal(route_hours_tenths) / Decimal("10"))
        * (Decimal(engaged_rate_cents_per_hour) / Decimal("100"))
    )
    mileage_floor_cents = _money_to_cents(
        (Decimal(business_miles_tenths) / Decimal("10"))
        * CALIFORNIA_PROP22_PER_MILE_RATE
    )
    estimated_floor_cents = engaged_time_floor_cents + mileage_floor_cents
    estimated_difference_cents = actual_pay_cents - estimated_floor_cents
    estimated_payment_cents = max(-estimated_difference_cents, 0)

    status = (
        "Informational only; uses route hours and business miles as proxies for engaged time "
        "and engaged miles and uses the statewide California minimum wage only."
    )

    return {
        "prop22_route_hours_tenths": route_hours_tenths,
        "prop22_business_miles_tenths": business_miles_tenths,
        "prop22_minimum_pay_rate_cents_per_hour": engaged_rate_cents_per_hour,
        "prop22_mileage_rate_cents_per_mile": mileage_rate_cents_per_mile,
        "prop22_engaged_time_floor_cents": engaged_time_floor_cents,
        "prop22_mileage_floor_cents": mileage_floor_cents,
        "prop22_estimated_floor_cents": estimated_floor_cents,
        "prop22_actual_pay_cents": actual_pay_cents,
        "prop22_estimated_difference_cents": estimated_difference_cents,
        "prop22_estimated_payment_cents": estimated_payment_cents,
        "prop22_status": status,
    }


def calculate_california_tax(state_inputs: dict, filing_status: str) -> dict:
    estimated_federal_agi_cents = state_inputs["estimated_federal_agi_cents"]
    estimated_california_agi_cents = estimated_federal_agi_cents
    california_adjustments_cents = 0
    standard_deduction_cents = CALIFORNIA_STANDARD_DEDUCTION_CENTS[filing_status]
    california_taxable_income_cents = max(estimated_california_agi_cents - standard_deduction_cents, 0)

    if california_taxable_income_cents <= 10_000_000:
        california_tax_before_credits_cents = _calculate_california_tax_from_table(
            california_taxable_income_cents,
            filing_status,
        )
    else:
        california_tax_before_credits_cents = _calculate_california_tax_from_schedule(
            california_taxable_income_cents,
            filing_status,
        )
    personal_exemption_credit_cents = _calculate_personal_exemption_credit(
        estimated_california_agi_cents,
        filing_status,
    )

    behavioral_health_services_tax_cents = 0
    if california_taxable_income_cents > CALIFORNIA_BHST_THRESHOLD_CENTS:
        taxable_over_threshold_dollars = Decimal(
            california_taxable_income_cents - CALIFORNIA_BHST_THRESHOLD_CENTS
        ) / Decimal("100")
        behavioral_health_services_tax_cents = _money_to_cents(
            taxable_over_threshold_dollars * CALIFORNIA_BHST_RATE
        )

    estimated_california_state_tax_cents = max(
        california_tax_before_credits_cents - personal_exemption_credit_cents,
        0,
    ) + behavioral_health_services_tax_cents

    threshold_cents = CALIFORNIA_ESTIMATED_PAYMENT_THRESHOLD_CENTS[filing_status]
    threshold_gap_cents = threshold_cents - estimated_california_state_tax_cents
    if threshold_gap_cents >= 0:
        threshold_gap_dollars = Decimal(threshold_gap_cents) / Decimal("100")
        california_status = (
            "Below California estimated quarterly payment threshold by "
            f"${threshold_gap_dollars:.2f}; simplified resident estimate"
        )
    else:
        threshold_over_dollars = Decimal(-threshold_gap_cents) / Decimal("100")
        california_status = (
            "California estimated quarterly payment threshold exceeded by "
            f"${threshold_over_dollars:.2f}; simplified resident estimate"
        )

    bhst_status = (
        "Not triggered"
        if behavioral_health_services_tax_cents == 0
        else f"Included in estimate: ${Decimal(behavioral_health_services_tax_cents) / Decimal('100'):.2f}"
    )

    return {
        "state_starting_income_cents": estimated_california_agi_cents,
        "state_business_income_deduction_cents": california_adjustments_cents,
        "state_taxable_business_income_cents": california_taxable_income_cents,
        "estimated_state_tax_cents": estimated_california_state_tax_cents,
        "state_status": california_status,
        "school_district_tax_status": bhst_status,
        **_calculate_california_prop22_info(state_inputs),
    }
