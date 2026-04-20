from __future__ import annotations

from decimal import Decimal

STATE_CODE = "pennsylvania"
STATE_NAME = "Pennsylvania"
STATE_TAX_FRAME_TITLE = "Pennsylvania Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated Pennsylvania State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "Pennsylvania Net Profits",
    "state_business_income_deduction_cents": "Pennsylvania Adjustments",
    "state_taxable_business_income_cents": "Pennsylvania Taxable Income",
    "estimated_state_tax_cents": "Estimated Pennsylvania State Tax",
    "state_status": "Pennsylvania Status",
    "school_district_tax_status": "Local Earned Income Tax",
}

PENNSYLVANIA_PERSONAL_INCOME_TAX_RATE = Decimal("0.0307")
PENNSYLVANIA_ESTIMATED_PAYMENT_INCOME_THRESHOLD_CENTS = 1_400_000


def calculate_pennsylvania_tax(state_inputs: dict, filing_status: str) -> dict:
    del filing_status

    pennsylvania_net_profits_cents = max(state_inputs["net_business_profit_cents"], 0)
    pennsylvania_adjustments_cents = 0
    pennsylvania_taxable_income_cents = pennsylvania_net_profits_cents
    estimated_pennsylvania_state_tax_cents = int(
        (
            (Decimal(pennsylvania_taxable_income_cents) / Decimal("100"))
            * PENNSYLVANIA_PERSONAL_INCOME_TAX_RATE
            * Decimal("100")
        ).quantize(Decimal("1"))
    )

    threshold_gap_cents = (
        PENNSYLVANIA_ESTIMATED_PAYMENT_INCOME_THRESHOLD_CENTS - pennsylvania_taxable_income_cents
    )
    if threshold_gap_cents >= 0:
        threshold_gap_dollars = Decimal(threshold_gap_cents) / Decimal("100")
        pennsylvania_status = (
            "Below Pennsylvania estimated quarterly payment threshold by "
            f"${threshold_gap_dollars:.2f} of Pennsylvania taxable income; simplified resident estimate"
        )
    else:
        threshold_over_dollars = Decimal(-threshold_gap_cents) / Decimal("100")
        pennsylvania_status = (
            "Pennsylvania estimated quarterly payment threshold exceeded by "
            f"${threshold_over_dollars:.2f} of Pennsylvania taxable income; simplified resident estimate"
        )

    return {
        "state_starting_income_cents": pennsylvania_net_profits_cents,
        "state_business_income_deduction_cents": pennsylvania_adjustments_cents,
        "state_taxable_business_income_cents": pennsylvania_taxable_income_cents,
        "estimated_state_tax_cents": estimated_pennsylvania_state_tax_cents,
        "state_status": pennsylvania_status,
        "school_district_tax_status": "No state-administered local earned income tax included",
    }
