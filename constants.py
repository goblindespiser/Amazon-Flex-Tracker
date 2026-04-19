from decimal import Decimal

APP_NAME = "Amazon Flex Tracker"
APP_FOLDER_NAME = "FlexTrack"
DATE_FMT = "%Y-%m-%d"

EXPENSE_CATEGORIES = (
    "Accessories",
    "Car Maintenance",
    "Delivery Equipment",
    "Equipment",
    "Miscellaneous",
    "Office/Printing",
    "Parking",
    "Phone/Service",
    "Supplies",
    "Tolls",
)

TAX_YEAR = 2026
DEFAULT_FILING_STATUS = "single"
TAX_DISCLAIMER = (
    "The app assumes Amazon Flex is the user's only income, assumes no withholding, "
    "no credits, no itemized deductions, no unusual adjustments, and no school district tax. "
    "The app uses the filing status you select and assumes you qualify for it. "
    "Dependent-related credits are not calculated."
)
TAX_SCOPE_NOTE = "Calculated using all logs through the selected month, including the selected month."

FILING_STATUS_LABELS = {
    "single": "Single",
    "married_filing_jointly": "Married Filing Jointly",
    "married_filing_separately": "Married Filing Separately",
    "head_of_household": "Head of Household",
    "qualifying_surviving_spouse": "Qualifying Surviving Spouse",
}

FEDERAL_STANDARD_DEDUCTION_CENTS = {
    "single": 1_610_000,
    "married_filing_jointly": 3_220_000,
    "married_filing_separately": 1_610_000,
    "head_of_household": 2_415_000,
    "qualifying_surviving_spouse": 3_220_000,
}

FEDERAL_BRACKETS_CENTS = {
    "single": [
        (1_240_000, Decimal("0.10")),
        (5_040_000, Decimal("0.12")),
        (10_570_000, Decimal("0.22")),
        (20_177_500, Decimal("0.24")),
        (25_622_500, Decimal("0.32")),
        (64_060_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    "married_filing_jointly": [
        (2_480_000, Decimal("0.10")),
        (10_080_000, Decimal("0.12")),
        (21_140_000, Decimal("0.22")),
        (40_355_000, Decimal("0.24")),
        (51_245_000, Decimal("0.32")),
        (76_870_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    "married_filing_separately": [
        (1_240_000, Decimal("0.10")),
        (5_040_000, Decimal("0.12")),
        (10_570_000, Decimal("0.22")),
        (20_177_500, Decimal("0.24")),
        (25_622_500, Decimal("0.32")),
        (38_435_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    "head_of_household": [
        (1_770_000, Decimal("0.10")),
        (6_745_000, Decimal("0.12")),
        (10_570_000, Decimal("0.22")),
        (20_175_000, Decimal("0.24")),
        (25_620_000, Decimal("0.32")),
        (64_060_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
    "qualifying_surviving_spouse": [
        (2_480_000, Decimal("0.10")),
        (10_080_000, Decimal("0.12")),
        (21_140_000, Decimal("0.22")),
        (40_355_000, Decimal("0.24")),
        (51_245_000, Decimal("0.32")),
        (76_870_000, Decimal("0.35")),
        (None, Decimal("0.37")),
    ],
}

STANDARD_MILEAGE_RATE_PER_MILE = Decimal("0.725")
QBI_DEDUCTION_RATE = Decimal("0.20")
SE_NET_EARNINGS_FACTOR = Decimal("0.9235")
SE_SOCIAL_SECURITY_RATE = Decimal("0.124")
SE_MEDICARE_RATE = Decimal("0.029")
SE_THRESHOLD_CENTS = 40_000
SOCIAL_SECURITY_WAGE_BASE_CENTS = 18_450_000
