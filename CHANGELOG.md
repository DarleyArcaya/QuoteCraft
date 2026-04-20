# Changelog
All notable changes to this project will be documented in this file.
## [1.1.2] - 2026-04-19

### Added
- **Banner update checker**: The app now checks for updates in the background and displays an update banner if a newer version is available.




## Old Version
## [1.1.0] - 2026-04-18

### Added
- **Company logo on quotes**: Users can now add their company logo in settings, which will always appear in the generated PDF files.
- **Setting / Save Data button**: Now the button save located in the settings page is on the top right corner.

### Fixed

- Fixed a bug that caused the app to crash
- fixed a bug that do not let the app translate from english to spanish correctly.
- In Settings / Company Names field, the word "Admin" will no longer appear for new users; the field will appear empty.

## [1.0.3] - 2026-04-11

### Added
- **Initial Public Release**: Core functionality of QuoteCraft.
- **Estimate Management**: Create, edit, search, and delete estimates with custom prefixes (EST, SC, JR).
- **PDF Generation**: Automatic generation of professional PDF documents for estimates.
- **Client Management**: Database to store and manage client contact information.
- **Financial Tracking**: Income management system linked to accepted estimates.
- **Internationalization (i18n)**: Full support for English and Spanish languages.
- **Theme Support**: Dark and Light mode integration based on user preference.
- **Backup System**: Manual backup and restore functionality for the SQLite database.
- **WhatsApp Integration**: Direct link to send estimate details to clients via WhatsApp.

### Technical Details
- Built with **Python** and **Flet** for cross-platform UI.
- Local storage using **SQLite**.
- - PDF styling and generation via **fpdf**.