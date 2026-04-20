from __future__ import annotations

from decimal import Decimal

STATE_CODE = "virginia"
STATE_NAME = "Virginia"
STATE_TAX_FRAME_TITLE = "Virginia Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated Virginia State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "Virginia Adjusted Gross Income",
    "state_business_income_deduction_cents": "Virginia Deductions and Exemptions",
    "state_taxable_business_income_cents": "Virginia Taxable Income",
    "estimated_state_tax_cents": "Estimated Virginia State Tax",
    "state_status": "Virginia Status",
    "school_district_tax_status": "Local Income Tax",
}

VIRGINIA_STANDARD_DEDUCTION_CENTS = {
    "single": 875_000,
    "married_filing_jointly": 1_750_000,
    "married_filing_separately": 875_000,
    "head_of_household": 875_000,
    "qualifying_surviving_spouse": 875_000,
}

VIRGINIA_PERSONAL_EXEMPTION_COUNT = {
    "single": 1,
    "married_filing_jointly": 2,
    "married_filing_separately": 1,
    "head_of_household": 1,
    "qualifying_surviving_spouse": 1,
}

VIRGINIA_PERSONAL_EXEMPTION_CENTS = 93_000
VIRGINIA_ESTIMATED_PAYMENT_THRESHOLD_CENTS = 100_000
VIRGINIA_TAX_SCHEDULE = [
    (300_000, Decimal("0.02"), 0),
    (500_000, Decimal("0.03"), 6_000),
    (1_700_000, Decimal("0.05"), 12_000),
    (None, Decimal("0.0575"), 72_000),
]


def _calculate_virginia_tax_from_schedule(taxable_income_cents: int) -> int:
    taxable_income_cents = max(taxable_income_cents, 0)
    lower_bound_cents = 0

    for upper_bound_cents, rate, base_tax_cents in VIRGINIA_TAX_SCHEDULE:
        if upper_bound_cents is None or taxable_income_cents <= upper_bound_cents:
            tax_dollars = (Decimal(base_tax_cents) / Decimal("100")) + (
                (Decimal(taxable_income_cents - lower_bound_cents) / Decimal("100")) * rate
            )
            return int((tax_dollars * Decimal("100")).quantize(Decimal("1")))
        lower_bound_cents = upper_bound_cents

    return 0


def calculate_virginia_tax(state_inputs: dict, filing_status: str) -> dict:
    virginia_agi_cents = max(state_inputs["estimated_federal_agi_cents"], 0)
    standard_deduction_cents = VIRGINIA_STANDARD_DEDUCTION_CENTS[filing_status]
    personal_exemptions_cents = VIRGINIA_PERSONAL_EXEMPTION_COUNT[filing_status] * VIRGINIA_PERSONAL_EXEMPTION_CENTS
    deductions_and_exemptions_cents = standard_deduction_cents + personal_exemptions_cents
    virginia_taxable_income_cents = max(virginia_agi_cents - deductions_and_exemptions_cents, 0)
    estimated_virginia_state_tax_cents = _calculate_virginia_tax_from_schedule(virginia_taxable_income_cents)

    threshold_gap_cents = VIRGINIA_ESTIMATED_PAYMENT_THRESHOLD_CENTS - estimated_virginia_state_tax_cents
    if threshold_gap_cents >= 0:
        threshold_gap_dollars = Decimal(threshold_gap_cents) / Decimal("100")
        virginia_status = (
            "Below Virginia estimated quarterly payment threshold by "
            f"${threshold_gap_dollars:.2f}; simplified resident estimate"
        )
    else:
        threshold_over_dollars = Decimal(-threshold_gap_cents) / Decimal("100")
        virginia_status = (
            "Virginia estimated quarterly payment threshold exceeded by "
            f"${threshold_over_dollars:.2f}; simplified resident estimate"
        )

    return {
        "state_starting_income_cents": virginia_agi_cents,
        "state_business_income_deduction_cents": deductions_and_exemptions_cents,
        "state_taxable_business_income_cents": virginia_taxable_income_cents,
        "estimated_state_tax_cents": estimated_virginia_state_tax_cents,
        "state_status": virginia_status,
        "school_district_tax_status": "No state-administered local income tax included",
    }
