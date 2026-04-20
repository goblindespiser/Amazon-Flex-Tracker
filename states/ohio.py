from __future__ import annotations

from decimal import Decimal

STATE_CODE = "ohio"
STATE_NAME = "Ohio"
STATE_TAX_FRAME_TITLE = "Ohio Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated Ohio State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "Ohio Qualifying Business Income",
    "state_business_income_deduction_cents": "Ohio Business Income Deduction",
    "state_taxable_business_income_cents": "Ohio Taxable Business Income",
    "estimated_state_tax_cents": "Estimated Ohio State Tax",
    "state_status": "Ohio Status",
    "school_district_tax_status": "School District Tax",
}

OHIO_BUSINESS_INCOME_DEDUCTION_LIMIT_CENTS = {
    "single": 25_000_000,
    "married_filing_jointly": 25_000_000,
    "married_filing_separately": 12_500_000,
    "head_of_household": 25_000_000,
    "qualifying_surviving_spouse": 25_000_000,
}

OHIO_BUSINESS_TAX_RATE = Decimal("0.03")
OHIO_ESTIMATED_PAYMENT_THRESHOLD_CENTS = 50_000


def calculate_ohio_tax(state_inputs: dict, filing_status: str) -> dict:
    # Ohio's business income deduction is based on qualifying business income,
    # not federal AGI after above-the-line adjustments like half of SE tax.
    ohio_starting_income_cents = max(state_inputs["net_business_profit_cents"], 0)
    ohio_business_income_deduction_cents = min(
        ohio_starting_income_cents,
        OHIO_BUSINESS_INCOME_DEDUCTION_LIMIT_CENTS[filing_status],
    )
    ohio_taxable_business_income_cents = max(
        ohio_starting_income_cents - ohio_business_income_deduction_cents,
        0,
    )
    estimated_ohio_state_tax_cents = int(
        (
            (Decimal(ohio_taxable_business_income_cents) / Decimal("100"))
            * OHIO_BUSINESS_TAX_RATE
            * Decimal("100")
        ).quantize(Decimal("1"))
    )
    threshold_gap_cents = OHIO_ESTIMATED_PAYMENT_THRESHOLD_CENTS - estimated_ohio_state_tax_cents
    if threshold_gap_cents >= 0:
        threshold_gap_dollars = Decimal(threshold_gap_cents) / Decimal("100")
        ohio_status = (
            "Below Ohio estimated quarterly payment threshold by "
            f"${threshold_gap_dollars:.2f}"
        )
    else:
        threshold_over_dollars = Decimal(-threshold_gap_cents) / Decimal("100")
        ohio_status = (
            "Ohio estimated quarterly payment threshold exceeded by "
            f"${threshold_over_dollars:.2f}"
        )

    return {
        "state_starting_income_cents": ohio_starting_income_cents,
        "state_business_income_deduction_cents": ohio_business_income_deduction_cents,
        "state_taxable_business_income_cents": ohio_taxable_business_income_cents,
        "estimated_state_tax_cents": estimated_ohio_state_tax_cents,
        "state_status": ohio_status,
        "school_district_tax_status": "Excluded by assumption",
    }
