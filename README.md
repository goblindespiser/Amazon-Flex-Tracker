# flex-track

A local desktop Amazon Flex bookkeeping and tax-estimate tool built with Python, Tkinter, and SQLite. The current downloadable build is the v0.1.1 portable ZIP.

## Current features
- Daily log entry
- Other expense tracking
- Summary view
- Tax estimate view
- Federal estimate with self-employment tax and simplified QBI deduction
- Multi-state tax estimate support
- California Prop 22 informational estimate panel
- CSV export
- Local backups

## Privacy and resource use
- Local-only desktop app built with Python, Tkinter, and SQLite.
- No cloud sync, no web API calls, no analytics, and no background service.
- Data is stored on the user's machine in the app data folder.
- Windows default storage path: `%LOCALAPPDATA%\\FlexTrack\\flex_tracker.db`
- Windows backup folder: `%LOCALAPPDATA%\\FlexTrack\\backups`
- Windows export folder: `%LOCALAPPDATA%\\FlexTrack\\exports`
- The app uses only Python standard-library modules in this repository, so runtime overhead stays low.

## Tax estimate scope
This app is a simplified estimator, not tax filing software.

Current tax assumptions:
- Amazon Flex is the user's only income
- no withholding
- no credits
- no itemized deductions
- no unusual adjustments
- no school district tax
- the user qualifies for the filing status they select
- dependent-related credits are not calculated

Federal notes:
- The federal estimate includes self-employment tax and a simplified QBI estimate under the app's assumptions.
- Additional Medicare Tax is not currently modeled.

State notes:
- Supported states: Ohio, California, Texas, Florida, Illinois, Virginia, Pennsylvania, North Carolina, and New York
- California includes a separate Prop 22 informational estimate panel
- State calculations are simplified resident estimates and do not attempt to cover every edge case

## Download & Installation
1. Direct link to the latest release: https://github.com/goblindespiser/flex-track/releases/tag/v0.1.1
2. Click "FlexTrack.zip" to begin download to desired destination folder
3. Extract zip
4. Open extracted folder
5. Double click FlexTrack.exe to run

## How to run tests
From the project folder, run:

```bat
python -m unittest discover -s tests -v
```

This runs the current unit tests for helper functions and tax calculations.
