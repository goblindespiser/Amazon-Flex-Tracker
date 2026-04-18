# flex-track

A local desktop Amazon Flex bookkeeping and tax-estimate tool built with Python, Tkinter, and SQLite. The current downloadable build is the v0.1.0 portable ZIP.

## Current features
- Daily log entry
- Other expense tracking
- Summary view
- Tax estimate view
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

## Notes
This is a public pre-release build. It is not tax filing software. Double check estimates. For State estimates, the only supported state at this time is Ohio. 

## Download & Installation
1. Direct link to the latest release: https://github.com/goblindespiser/flex-tracker/releases/tag/v0.1.0
2. Click "FlexTrack.zip" to begin download to desired destination folder
3. Extract zip
4. Open extracted folder
5. Double click FlexTrack.exe to run
