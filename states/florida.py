from __future__ import annotations

STATE_CODE = "florida"
STATE_NAME = "Florida"
STATE_TAX_FRAME_TITLE = "Florida Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated Florida State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "Florida Taxable Income",
    "state_business_income_deduction_cents": "Florida Adjustments",
    "state_taxable_business_income_cents": "Florida Taxable Income",
    "estimated_state_tax_cents": "Estimated Florida State Tax",
    "state_status": "Florida Status",
    "school_district_tax_status": "Local Income Tax",
}


def calculate_florida_tax(state_inputs: dict, filing_status: str) -> dict:
    del filing_status

    taxable_income_cents = max(state_inputs["net_business_profit_cents"], 0)

    return {
        "state_starting_income_cents": taxable_income_cents,
        "state_business_income_deduction_cents": 0,
        "state_taxable_business_income_cents": taxable_income_cents,
        "estimated_state_tax_cents": 0,
        "state_status": "Florida has no state individual income tax under this app's assumptions",
        "school_district_tax_status": "No state-administered local income tax included",
    }
