# Subscription Expense Monitoring System

A full-stack web application built with Django and PostgreSQL for tracking recurring digital subscriptions, automating multi-currency expense conversion, and analyzing personal financial metrics.

## Overview

Managing multiple digital subscriptions across different currencies (USD, EUR, UAH) often leads to untracked recurring expenses. This system provides a centralized dashboard that automatically converts foreign currency subscriptions into UAH using live banking exchange rates, monitors upcoming billing cycles, and visualizes monthly spending distribution.

## Key Engineering Features

* **Live Currency Conversion & Caching:** Integrates with the **Monobank Public API** to fetch real-time USD and EUR exchange rates (ISO 4217 standard) and caches them in PostgreSQL.
* **Three-Tier Fallback Mechanism (Fault Tolerance):** Ensures uninterrupted expense calculation even if the external banking API is unreachable or rate-limited:
  1. Attempts to fetch fresh exchange rates from the Monobank API.
  2. Falls back to the most recent cached rate in the PostgreSQL database upon network failure.
  3. Uses predefined baseline rates if no historical database records exist.
* **Financial Precision:** Uses fixed-point `Decimal` arithmetic (`DecimalField`) across models and business logic to prevent floating-point rounding errors during currency conversion.
* **Automated Payment Risk Assessment:** Dynamically computes the time delta ($\Delta t = \text{Date}_{\text{payment}} - \text{Date}_{\text{current}}$) for each subscription and classifies billing urgency into four states: `normal`, `warning` ($\le 3$ days), `critical` ($1$ day), and `overdue` ($< 0$ days).
* **Database-Level Analytics:** Leverages Django ORM aggregations (`annotate`, `Sum`) to compute category-based spending breakdowns, top-5 most expensive services, and chronological monthly expense projections.
* **Role-Based Access & Custom Admin Dashboard:** Implements user authentication, isolated user workspaces, and a dedicated superuser dashboard featuring global system metrics, username search (`icontains`), multi-criteria sorting, and query slicing for performance optimization.

## Tech Stack

* **Backend:** Python 3, Django
* **Database:** PostgreSQL
* **External Integration:** Monobank API (`requests`)
* **Frontend:** HTML5, CSS3, Django Templates
* **Configuration & Security:** `python-dotenv` (Environment variable isolation)

## Project Structure

```text
subscription_monitor/
├── config/                  # Project configuration, URL routing, WSGI/ASGI
├── subscriptions/
│   ├── migrations/          # Database schema migrations
│   ├── static/              # CSS styles and static assets
│   ├── templates/           # HTML templates (Dashboard, Analytics, Auth, Admin)
│   ├── models.py            # Database models (Category, ExchangeRate, Subscription)
│   ├── services.py          # Business logic & Monobank API integration
│   ├── views.py             # Controllers, ORM analytics, and access control
│   └── urls.py              # Application-level routing
├── .env.example             # Template for environment variables
├── .gitignore               # Git exclusion rules
├── manage.py                # Django CLI utility
└── requirements.txt         # Project dependencies 
```

Local Setup & Installation
1. Clone the repository
Bash
git clone [https://github.com/alekspvlnk/subscription-monitor.git](https://github.com/alekspvlnk/subscription-monitor.git)
cd subscription-monitor
2. Create and activate a virtual environment
Bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
3. Install dependencies
Bash
pip install -r requirements.txt
4. Configure environment variables
Create a .env file in the project root based on .env.example:

```text
SECRET_KEY=your_secret_key_here
DEBUG=True

DB_NAME=subscription_db
DB_USER=postgres
DB_PASSWORD=your_db_password_here
DB_HOST=localhost
DB_PORT=5432
```

5. Apply database migrations and run the server
```Bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/.