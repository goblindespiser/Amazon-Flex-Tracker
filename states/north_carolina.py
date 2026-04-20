from __future__ import annotations

from decimal import Decimal

STATE_CODE = "north_carolina"
STATE_NAME = "North Carolina"
STATE_TAX_FRAME_TITLE = "North Carolina Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated North Carolina State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "North Carolina AGI",
    "state_business_income_deduction_cents": "North Carolina Standard Deduction",
    "state_taxable_business_income_cents": "North Carolina Taxable Income",
    "estimated_state_tax_cents": "Estimated North Carolina State Tax",
    "state_status": "North Carolina Status",
    "school_district_tax_status": "Local Income Tax",
}

NORTH_CAROLINA_INDIVIDUAL_INCOME_TAX_RATE = Decimal("0.0399")
NORTH_CAROLINA_ESTIMATED_PAYMENT_THRESHOLD_CENTS = 100_000
NORTH_CAROLINA_STANDARD_DEDUCTION_CENTS = {
    "single": 1_275_000,
    "married_filing_jointly": 2_550_000,
    "married_filing_separately": 1_275_000,
    "head_of_household": 1_912_500,
    "qualifying_surviving_spouse": 2_550_000,
}


def calculate_north_carolina_tax(state_inputs: dict, filing_status: str) -> dict:
    north_carolina_agi_cents = max(state_inputs["estimated_federal_agi_cents"], 0)
    north_carolina_standard_deduction_cents = NORTH_CAROLINA_STANDARD_DEDUCTION_CENTS[filing_status]
    north_carolina_taxable_income_cents = max(
        north_carolina_agi_cents - north_carolina_standard_deduction_cents,
        0,
    )
    estimated_north_carolina_state_tax_cents = int(
        (
            (Decimal(north_carolina_taxable_income_cents) / Decimal("100"))
            * NORTH_CAROLINA_INDIVIDUAL_INCOME_TAX_RATE
            * Decimal("100")
        ).quantize(Decimal("1"))
    )

    threshold_gap_cents = (
        NORTH_CAROLINA_ESTIMATED_PAYMENT_THRESHOLD_CENTS - estimated_north_carolina_state_tax_cents
    )
    if threshold_gap_cents >= 0:
        threshold_gap_dollars = Decimal(threshold_gap_cents) / Decimal("100")
        north_carolina_status = (
            "Below North Carolina estimated quarterly payment threshold by "
            f"${threshold_gap_dollars:.2f}; simplified resident estimate"
        )
    else:
        threshold_over_dollars = Decimal(-threshold_gap_cents) / Decimal("100")
        north_carolina_status = (
            "North Carolina estimated quarterly payment threshold exceeded by "
            f"${threshold_over_dollars:.2f}; simplified resident estimate"
        )

    return {
        "state_starting_income_cents": north_carolina_agi_cents,
        "state_business_income_deduction_cents": north_carolina_standard_deduction_cents,
        "state_taxable_business_income_cents": north_carolina_taxable_income_cents,
        "estimated_state_tax_cents": estimated_north_carolina_state_tax_cents,
        "state_status": north_carolina_status,
        "school_district_tax_status": "No state-administered local income tax included",
    }
