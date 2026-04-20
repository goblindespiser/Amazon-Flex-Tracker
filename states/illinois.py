from __future__ import annotations

from decimal import Decimal

STATE_CODE = "illinois"
STATE_NAME = "Illinois"
STATE_TAX_FRAME_TITLE = "Illinois Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated Illinois State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "Illinois Net Income",
    "state_business_income_deduction_cents": "Illinois Adjustments",
    "state_taxable_business_income_cents": "Illinois Taxable Income",
    "estimated_state_tax_cents": "Estimated Illinois State Tax",
    "state_status": "Illinois Status",
    "school_district_tax_status": "Local Income Tax",
}

ILLINOIS_INDIVIDUAL_INCOME_TAX_RATE = Decimal("0.0495")
ILLINOIS_ESTIMATED_PAYMENT_THRESHOLD_CENTS = 100_000


def calculate_illinois_tax(state_inputs: dict, filing_status: str) -> dict:
    del filing_status

    illinois_net_income_cents = max(state_inputs["estimated_federal_agi_cents"], 0)
    illinois_adjustments_cents = 0
    illinois_taxable_income_cents = illinois_net_income_cents
    estimated_illinois_state_tax_cents = int(
        (
            (Decimal(illinois_taxable_income_cents) / Decimal("100"))
            * ILLINOIS_INDIVIDUAL_INCOME_TAX_RATE
            * Decimal("100")
        ).quantize(Decimal("1"))
    )
    threshold_gap_cents = ILLINOIS_ESTIMATED_PAYMENT_THRESHOLD_CENTS - estimated_illinois_state_tax_cents
    if threshold_gap_cents >= 0:
        threshold_gap_dollars = Decimal(threshold_gap_cents) / Decimal("100")
        illinois_status = (
            "Below Illinois estimated quarterly payment threshold by "
            f"${threshold_gap_dollars:.2f}; simplified resident estimate"
        )
    else:
        threshold_over_dollars = Decimal(-threshold_gap_cents) / Decimal("100")
        illinois_status = (
            "Illinois estimated quarterly payment threshold exceeded by "
            f"${threshold_over_dollars:.2f}; simplified resident estimate"
        )

    return {
        "state_starting_income_cents": illinois_net_income_cents,
        "state_business_income_deduction_cents": illinois_adjustments_cents,
        "state_taxable_business_income_cents": illinois_taxable_income_cents,
        "estimated_state_tax_cents": estimated_illinois_state_tax_cents,
        "state_status": illinois_status,
        "school_district_tax_status": "No state-administered local income tax included",
    }
