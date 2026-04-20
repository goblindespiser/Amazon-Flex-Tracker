from __future__ import annotations

"""
Copy this file when adding a new state module.

Recommended workflow:
1. Copy this file to `states/<state_code>.py`
2. Replace the placeholder names and labels
3. Fill in the state-specific constants
4. Keep the assumptions simple and consistent with the app disclaimer
5. Return the standard result keys expected by the UI/export code

This template is intentionally minimal. It is meant for simple resident
estimates under the app's stated assumptions, not full tax-prep logic.
"""

STATE_CODE = "template_state"
STATE_NAME = "Template State"
STATE_TAX_FRAME_TITLE = "Template State Estimate (State Only)"
STATE_ESTIMATED_TAX_LABEL = "Estimated Template State Tax"
STATE_FIELD_LABELS = {
    "state_starting_income_cents": "Template State Starting Income",
    "state_business_income_deduction_cents": "Template State Adjustments",
    "state_taxable_business_income_cents": "Template State Taxable Income",
    "estimated_state_tax_cents": "Estimated Template State Tax",
    "state_status": "Template State Status",
    "school_district_tax_status": "Local Tax Status",
}


def calculate_template_state_tax(state_inputs: dict, filing_status: str) -> dict:
    """
    Required inputs currently passed from app.py:
    - estimated_federal_agi_cents
    - deductible_half_se_tax_cents
    - estimated_self_employment_tax_cents
    - gross_business_income_cents
    - net_business_profit_cents
    - business_miles_tenths
    - deductible_tolls_parking_cents

    Use only the inputs your state logic actually needs.
    """

    estimated_federal_agi_cents = state_inputs["estimated_federal_agi_cents"]

    # Replace these placeholders with real state logic.
    state_starting_income_cents = max(estimated_federal_agi_cents, 0)
    state_adjustments_cents = 0
    state_taxable_income_cents = state_starting_income_cents
    estimated_state_tax_cents = 0

    status = "Not yet implemented"
    local_tax_status = "Excluded by assumption"

    return {
        "state_starting_income_cents": state_starting_income_cents,
        "state_business_income_deduction_cents": state_adjustments_cents,
        "state_taxable_business_income_cents": state_taxable_income_cents,
        "estimated_state_tax_cents": estimated_state_tax_cents,
        "state_status": status,
        "school_district_tax_status": local_tax_status,
    }
