# State Module Template

Each state file in this folder should stay simple and follow the same shape.

## What every state file needs
- `STATE_CODE`
- `STATE_NAME`
- `STATE_TAX_FRAME_TITLE`
- `STATE_ESTIMATED_TAX_LABEL`
- `STATE_FIELD_LABELS`
- one calculation function that returns the standard result keys

## Standard result keys
- `state_starting_income_cents`
- `state_business_income_deduction_cents`
- `state_taxable_business_income_cents`
- `estimated_state_tax_cents`
- `state_status`
- `school_district_tax_status`

## Recommended process for a new state
1. Copy [states/_template.py](/C:/Users/Owner/Downloads/Amazon%20Flex%20Tracker/states/_template.py:1) to `states/<state_code>.py`
2. Rename the calculation function
3. Replace the labels and constants with state-specific values
4. Keep the logic within the app's existing assumptions
5. Import the module in [states/__init__.py](/C:/Users/Owner/Downloads/Amazon%20Flex%20Tracker/states/__init__.py:1)
6. Add the module to `STATE_MODULES`
7. Add at least one focused unit test in [tests/test_app.py](/C:/Users/Owner/Downloads/Amazon%20Flex%20Tracker/tests/test_app.py:1)

## Scope guidance
This app is a simplified estimator, not full tax-prep software.

When adding a state, prefer:
- resident estimate logic
- standard deduction path when that matches the app assumptions
- broad, common-case rules
- clear status text for excluded items

Avoid unless broadly useful:
- rare credits
- complex residency edge cases
- unusual one-off adjustments
- full local-tax systems unless they matter to a large share of users

## Existing examples
- [states/ohio.py](/C:/Users/Owner/Downloads/Amazon%20Flex%20Tracker/states/ohio.py:1)
- [states/california.py](/C:/Users/Owner/Downloads/Amazon%20Flex%20Tracker/states/california.py:1)
