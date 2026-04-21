# QuoteCraft

**QuoteCraft** is a desktop application to manage business estimates and personal finances. It is built with **Python** and **Flet**, featuring a clean design.

<div align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flet-045592?style=for-the-badge&logo=flutter&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" />
</div>

---

## Main Features

* **Estimate Management:** Create and edit professional estimates for clients.
* **PDF Export:** Generate clean PDF documents ready to send.
* **Multi-language Support:** Works in **English** and **Spanish** (with support for accents and special characters).
* **Finance Control:** Track income, expenses, and taxes. Export annual financial reports.
* **Modern UI:** Simple and intuitive interface with rounded corners and smooth navigation.

---

## Screenshots

<p align="center">
  <h3>1. Main Menu</h3>
  <img src="source/screenshots/menu.png" width="750" alt="Main Menu" style="border-radius: 10px;"/>
</p>

<p align="center">
  <h3>2. Create Estimate</h3>
  <img src="source/screenshots/create estimate.png" width="750" alt="Create Estimate" style="border-radius: 10px;"/>
</p>

<p align="center">
  <h3>3. Manage Finances</h3>
  <img src="source/screenshots/manage finances.png" width="750" alt="Manage Finances" style="border-radius: 10px;"/>
</p>

<p align="center">
  <h3>4. Manage Clients</h3>
  <img src="source/screenshots/manage clients.png" width="750" alt="Manage Clients" style="border-radius: 10px;"/>
</p>

<p align="center">
  <h3>5. Calendar View</h3>
  <img src="source/screenshots/calendar.png" width="750" alt="Calendar View" style="border-radius: 10px;"/>
</p>

---

## Tech Stack

* **Python**: Core programming language.
* **Flet**: UI framework (Flutter-based).
* **FPDF**: PDF generation.
* **SQLite**: Local database storage.

---

## ⚙️ Installation

### 🚀 Quick Start

Clone the repository and install dependencies depending on your operating system.

---

### Windows

```bash

# Clone the repository
git clone https://github.com/DarleyArcaya/QuoteCraft.git

# Enter project folder
cd QuoteCraft

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

``` 
### MacOS

```bash
# Clone the repository
git clone https://github.com/DarleyArcaya/QuoteCraft.git

# Enter project folder
cd QuoteCraft

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

```

### Linux
# Linux support note

### The application is NOT fully configured for Linux yet.
### The issue is related to the local database path not being automatically created on Linux systems. This will be fixed in a future update.
```bash
# Clone the repository
git clone https://github.com/DarleyArcaya/QuoteCraft.git

# Enter project folder
cd QuoteCraft

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

```

## Project Structure

All source code is inside the `/source` directory:

* **`views/`**: UI screens and Flet components.
* **`services/`**: Business logic, PDF generation, calculations.
* **`utils/`**: Helper functions and utilities.
* **`database/`**: Database connection and SQL management.
* **`locales/`**: Translation files (English/Spanish).
* **`assets/`**: Images, logos, branding.
* **`screenshots/`**: App images used in README.
* **`data/`**: Local app data storage.
* **`backups/`**: Local backups and snapshots.
* **`pdfs/`**: Generated PDF output folder.

---

## Main Files

* `source/main.py`: Entry point of the application.
* `requirements.txt`: Python dependencies.
* `flet.yaml`: Flet configuration.
* `LICENSE`: Software license.
* `CHANGELOG.md`: Update history.
* `.gitignore`: Files ignored by Git.

---

## Why QuoteCraft?

I built this tool to bridge the gap between complex accounting software and simple spreadsheets. The goal was to create a lightweight, cross-platform solution with a clean UI that small business owners can actually use.

---

## Connect with me

* [LinkedIn](https://www.linkedin.com/in/darley-s-0544262a1?utm_source=share_via&utm_content=profile&utm_medium=member_ios)

---

## Author

* **Darley Omar Silot Arcaya** - *Computer Science*

> [!NOTE]
> **QuoteCraft** is currently in active development. While the source code is available for review and educational purposes, we are exploring commercial features and official releases soon.