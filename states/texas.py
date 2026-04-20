from __future__ import annotations

STATE_CODE = "texas"
STATE_NAME = "Texas"
STATE_TAX_FRAME_TITLE = "Texas Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated Texas State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "Texas Taxable Income",
    "state_business_income_deduction_cents": "Texas Adjustments",
    "state_taxable_business_income_cents": "Texas Taxable Income",
    "estimated_state_tax_cents": "Estimated Texas State Tax",
    "state_status": "Texas Status",
    "school_district_tax_status": "Local Income Tax",
}


def calculate_texas_tax(state_inputs: dict, filing_status: str) -> dict:
    del filing_status

    taxable_income_cents = max(state_inputs["net_business_profit_cents"], 0)

    return {
        "state_starting_income_cents": taxable_income_cents,
        "state_business_income_deduction_cents": 0,
        "state_taxable_business_income_cents": taxable_income_cents,
        "estimated_state_tax_cents": 0,
        "state_status": "Texas has no state individual income tax under this app's assumptions",
        "school_district_tax_status": "No state-administered local income tax included",
    }
