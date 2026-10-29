# 🏦 Apex Bank Management System

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%20%2F%20SQLAlchemy-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

A modern, secure, and full-featured **Bank Management System** built with **Flask**, **SQLAlchemy**, and **Flask-Login**. The system features role-based access control (Customer, Branch Manager, and Administrator), multi-account management (Checking & Savings), comprehensive financial transactions, beneficiary management, cardless/ATM cash out, utility bill payments, and extended lifestyle financial services.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
  - [Customer Portal](#-customer-portal)
  - [Banking & Financial Services](#-banking--financial-services)
  - [Branch Manager Portal](#-branch-manager-portal)
  - [System Administrator Portal](#-system-administrator-portal)
- [Default Demo Credentials](#-default-demo-credentials)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Configuration & Environment Variables](#-configuration--environment-variables)
- [Services Catalog](#-services-catalog)
- [License](#-license)

---

## ✨ Key Features

### 👤 Customer Portal
- **Multi-Account Dashboard**: Real-time overview of active checking and high-yield savings accounts with balances and status.
- **Account Numbering**: Standard 13-digit account numbers (e.g., `1000XXXXXXXXX`).
- **Transaction History**: Filterable ledger with transaction reference IDs, dates, debit/credit indicators, and running balance tracking.
- **Beneficiaries Directory**: Save, organize, and quickly send money to trusted payees.

### 💸 Banking & Financial Services
- **Transfers**:
  - **Own Accounts Transfer**: Instant zero-fee movement between your Checking and Savings accounts.
  - **CBC Internal Transfer**: Instant transfers to other bank accounts using 13-digit CBC numbers.
  - **Other Bank Transfers (Wire / ACH)**: Interbank wire transfers with bank and routing details.
- **Cash Out Services**:
  - **ATM Cardless Cash Out**: Generate one-time secure OTP cashout tokens for ATM withdrawal without a physical card.
  - **CBC Agent / Branch Cash Out**: Fast point-of-sale or branch-assisted cash withdrawals.
- **Telecom & Airtime**:
  - Instant mobile airtime top-ups across supported cellular networks.
- **Lifestyle & Everyday Payments**:
  - **Utilities & Bills**: Electricity, water, internet, and municipal utility bills.
  - **Travel**: Airline bookings, railway tickets, and rideshare passes.
  - **Shopping**: E-commerce checkouts and retail merchant payments.
  - **Government Services**: Passport renewals, civic licensing, and municipal fee payments.
  - **Subscriptions**: Streaming, software, news, and entertainment recurring plans.
  - **Donations**: Verified charity and humanitarian cause contributions.
  - **Tax Payments**: Income, corporate, and property tax settlements.
  - **My Service**: Customizable on-demand service hub.

### 👔 Branch Manager Portal
- Comprehensive overview of all branch customer accounts.
- Audit live transactions across all customer accounts.
- Freeze, unfreeze, or suspend accounts for risk management and compliance.

### 🛡️ System Administrator Portal
- System-wide user administration (create, update, manage customers, managers, and admins).
- Global transaction auditing and security event monitoring.
- High-level platform metrics: total liquidity, transaction volume, active accounts, and user growth.

---

## 🔑 Default Demo Credentials

The application automatically seeds realistic demo data on the first run:

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `password123` | Full administrative and security controls |
| **Branch Manager** | `manager` | `password123` | Account auditing and compliance management |
| **Customer** | `customer` | `password123` | Pre-funded checking ($5,420.50) & savings ($14,850.00) accounts |
| **Customer (Secondary)** | `jordan` | `password123` | Secondary customer for inter-account wire testing ($3,200.00) |

---

## 🛠️ Tech Stack

- **Backend Framework**: [Flask](https://flask.palletsprojects.com/) (Python 3.10+)
- **ORM & Database**: [SQLAlchemy](https://www.sqlalchemy.org/) & [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) with SQLite (configurable to PostgreSQL / MySQL)
- **Authentication**: [Flask-Login](https://flask-login.readthedocs.io/) with salted password hashing ([Werkzeug](https://werkzeug.palletsprojects.com/))
- **Form Handling & Validation**: [Flask-WTF](https://flask-wtf.readthedocs.io/) & [WTForms](https://wtforms.readthedocs.io/)
- **Templating**: Jinja2 with modern modular layouts, cards, and modal dialogs
- **Frontend / Styling**: Vanilla CSS design system with responsive grid layout and dark-mode accents

---

## 📁 Project Structure

```text
Bank-Management-System/
├── app/
│   ├── __init__.py           # Flask app factory and blueprint registration
│   ├── extensions.py         # Extensions (db, login_manager)
│   ├── seed.py               # Database seeder for demo accounts and transactions
│   ├── forms/                # WTForms validation schemas
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── user.py           # User model (Customer, Manager, Admin)
│   │   ├── account.py        # Checking and Savings bank accounts
│   │   ├── transaction.py    # Ledger entries and transaction tracking
│   │   └── beneficiary.py    # Saved payee directory
│   ├── routes/               # Modular Flask blueprints
│   │   ├── main_routes.py    # Public landing page and information
│   │   ├── auth_routes.py    # Login, registration, and logout
│   │   ├── banking_routes.py # Dashboard, transactions, statements
│   │   ├── services_routes.py# Transfers, cashout, bills, lifestyle services
│   │   ├── manager_routes.py # Branch manager portal
│   │   └── admin_routes.py   # Admin management portal
│   ├── static/               # CSS stylesheets, JavaScript, and assets
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── auth/             # Login and signup views
│   │   ├── services/         # Banking services views
│   │   ├── manager/          # Manager portal views
│   │   ├── admin/            # Admin portal views
│   │   ├── dashboard.html    # Customer banking dashboard
│   │   └── index.html        # Public homepage
│   └── utils/                # Role-based decorators and helpers
├── instance/                 # SQLite database storage (bank_system.db)
├── config.py                 # Environment configurations (Dev / Prod)
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── package.json              # Optional NPM run scripts and project metadata
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: Version 3.10 or higher
- **pip**: Python package manager
- *(Optional)* **Node.js**: If using `npm run dev` convenience scripts

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/aregawibarambaras6-pixel/Bank-Managenet-System.git
   cd Bank-Management-System
   ```

2. **Create and activate a virtual environment**:
   - **Windows (Command Prompt / PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask development server**:
   ```bash
   python run.py
   ```
   *Or with npm (if Node.js is installed):*
   ```bash
   npm run dev
   ```

2. **Open in browser**:
   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

3. **Log in**:
   Use any of the [default demo credentials](#-default-demo-credentials) to explore the respective customer, manager, or admin dashboard.

---

## ⚙️ Configuration & Environment Variables

Settings can be customized via environment variables or a `.env` file:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `development` | Environment mode (`development` or `production`) |
| `SECRET_KEY` | *(Built-in dev key)* | Secret key for session security and CSRF tokens |
| `DATABASE_URL` | `sqlite:///instance/bank_system.db` | Database connection URI (SQLite, Postgres, etc.) |

---

## 📦 Services Catalog

| Category | Service | Description |
| :--- | :--- | :--- |
| **Transfers** | Own Transfer | Instant zero-fee transfers between user's accounts |
| | CBC Transfer | Peer-to-peer transfers to internal CBC bank accounts |
| | Other Bank Transfer | External transfers with routing and account details |
| **Withdrawals** | ATM Cash Out | Cardless withdrawal via generated secure token |
| | CBC Cash Out | In-branch / agent POS withdrawal |
| **Lifestyle** | Airtime Top-Up | Mobile phone credit top-ups |
| | Utility Payments | Electricity, water, internet, and cable |
| | Travel & Transport | Flight bookings, train tickets, ride vouchers |
| | Shopping & Retail | Merchant retail and e-commerce payments |
| | Government | Official fee payments, permits, licenses |
| | Subscriptions | Streaming, digital subscriptions, SaaS renewals |
| | Donations | Contributions to verified charities |
| | Tax Payments | Personal income and municipal property taxes |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
