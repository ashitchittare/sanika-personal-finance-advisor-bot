# Personal Finance Advisor Bot (FinBot)

A complete, full-stack personal finance web application with automated cashflow analytics, category budgeting, savings & milestone goal tracking, and an **AI Financial Advisor (FinBot)** powered by Google Gemini with an intelligent offline local fallback engine.

![Tech Stack](https://img.shields.io/badge/Stack-Flask_|_SQLAlchemy_|_SQLite_|_Bootstrap_5_|_Chart.js-blue)
![Currency](https://img.shields.io/badge/Currency-INR_(₹)-green)
![Tests](https://img.shields.io/badge/Tests-14_Passed_100%25-success)

---

## 🌟 Key Features

1. **User Authentication & Isolation**
   - Secure registration, login, logout, and session management using `Flask-Login` and `Werkzeug` PBKDF2 password hashing.
   - Strict multi-tenant data isolation: every income, expense, budget, savings deposit, and goal record belongs exclusively to the logged-in user.

2. **Interactive Financial Dashboard**
   - Live metrics: Total Income, Total Expenses, Current Savings, Net Balance, and Active Month Balance.
   - 6-month Income vs. Expense bar chart and current-month category breakdown doughnut chart powered by `Chart.js`.
   - Recent activity stream combining real-time income and expense entries.
   - Quick overview of active financial goals and progress meters.

3. **Income Management (Full CRUD)**
   - Add, edit, delete, and view income logs with source tagging (*Salary, Freelance, Investments, Business, etc.*), custom dates, and descriptions.

4. **Expense Management (Full CRUD)**
   - Record expenses across 9 standardized categories: *Food, Transport, Education, Rent, Shopping, Entertainment, Healthcare, Bills, Other*.
   - Filter transactions by category with dynamic sum recalculation.

5. **Monthly & Category Budget Planner**
   - Define monthly budget caps per expense category.
   - Visual progress indicators comparing actual spend vs. budgeted allocation.
   - Automatic **Overspending Alerts** (highlighted in red) when spending breaches the allocated threshold.

6. **Savings Tracker**
   - Log savings deposits with dates and investment notes (e.g., *Mutual Fund SIP, Emergency Fund, FD*).
   - Track monthly savings velocity and historical deposits.

7. **Financial Goals Tracker**
   - Set financial targets (*e.g., Emergency Reserve, MacBook Pro, Vacation Trip*), target completion dates, and target amounts.
   - Incrementally update saved amounts with dynamic progress bars and countdown timers.

8. **Monthly Reports & Analytics**
   - Monthly summary breakdowns with historical trend analysis over 6–12 months.
   - Category distribution, budget variance analysis, and Financial Health Scorecard (0–100 rating).

9. **FinBot AI Financial Advisor**
   - Dedicated AI advisor page analyzing real user database metrics.
   - Powered by **Google Gemini API** (`gemini-2.5-flash` / configurable model).
   - **Zero-Crash Local Fallback:** If `GEMINI_API_KEY` is not provided or network is offline, an intelligent rule-based engine generates rich, personalized financial recommendations and 50/30/20 budgeting advice directly from SQLite data.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug
- **Database:** SQLite with SQLAlchemy ORM (configured via dynamic absolute paths for local and cloud compatibility)
- **Frontend:** HTML5, CSS3 (Modern Slate & Emerald Theme), JavaScript (Vanilla ES6+), Bootstrap 5.3, Bootstrap Icons
- **Data Visualization:** Chart.js 4.4
- **AI Integration:** Google Gemini API (`google-genai` / `google.generativeai`) with built-in rule-based fallback
- **Testing:** Pytest (Unit, Integration, Isolation, and Lifecycle tests)
- **WSGI Production Server:** Gunicorn

---

## 📁 Project Structure

```
sanika personal finance advisor bot/
│
├── app/
│   ├── __init__.py               # Flask application factory (auto DB & instance creation)
│   ├── config.py                 # Environment-aware configuration (Dev, Test, Prod)
│   ├── extensions.py             # SQLAlchemy & LoginManager instances
│   │
│   ├── models/                   # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py               # User model & password hashing
│   │   ├── income.py             # Income model
│   │   ├── expense.py            # Expense model & categories
│   │   ├── budget.py             # Monthly category budget model
│   │   ├── savings.py            # Savings records model
│   │   └── goal.py               # Financial milestones & progress model
│   │
│   ├── routes/                   # Blueprints & Controllers
│   │   ├── __init__.py
│   │   ├── auth.py               # Register, Login, Logout
│   │   ├── dashboard.py          # Dashboard view
│   │   ├── income.py             # Income CRUD
│   │   ├── expense.py            # Expense CRUD
│   │   ├── budget.py             # Budget CRUD & comparison
│   │   ├── savings.py            # Savings tracking
│   │   ├── goals.py              # Financial goals management
│   │   ├── reports.py            # Analytics & reports
│   │   └── finbot.py             # FinBot AI chat & advisor API
│   │
│   ├── services/                 # Business logic & analytics
│   │   ├── __init__.py
│   │   ├── finance_analytics.py  # Overview, trends, health score, category stats
│   │   └── ai_advisor.py         # Gemini API client & intelligent local fallback
│   │
│   ├── static/                   # Static assets
│   │   ├── css/style.css         # Custom responsive stylesheet
│   │   └── js/
│   │       ├── charts.js         # Chart.js renderers
│   │       └── finbot.js         # Interactive FinBot chat client
│   │
│   └── templates/                # Jinja2 HTML Templates
│       ├── base.html             # Master layout with navigation & toast alerts
│       ├── dashboard.html        # Main dashboard
│       ├── auth/                 # Login & Register views
│       ├── income/               # Income list & form
│       ├── expense/              # Expense list & form
│       ├── budget/               # Budget planner
│       ├── savings/              # Savings tracker
│       ├── goals/                # Goals tracker & edit view
│       ├── reports/              # Visual reports
│       └── finbot/               # FinBot AI conversational interface
│
├── instance/                     # SQLite database directory (auto-created on startup)
│   └── finance.db
│
├── tests/                        # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures & isolated test client
│   ├── test_auth.py              # Registration, login, route protection
│   ├── test_crud.py              # Income, Expense, Budget, Savings, Goals CRUD
│   ├── test_calculations.py      # Aggregations, variance, health score
│   ├── test_isolation.py         # Cross-user authorization & isolation
│   ├── test_finbot.py            # AI advisor & local fallback tests
│   ├── test_db_init.py           # Clean database creation on missing directory
│   └── test_live_server.py       # Full end-to-end user lifecycle flow
│
├── run.py                        # Application entry point (0.0.0.0, PORT env)
├── seed_data.py                  # Idempotent demo database seeder
├── requirements.txt              # Production and development dependencies
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore file (excludes *.db, .env, etc.)
└── README.md                     # Comprehensive documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git

### 2. Clone and Setup Virtual Environment

```bash
# Clone the repository
git clone <repo-url>
cd "sanika personal finance advisor bot"

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (CMD):
.venv\Scripts\activate.bat
# On Linux / macOS:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Contents of `.env`:
```ini
# Flask Secret Key
SECRET_KEY=change-this-secret-key-for-production

# SQLite Database path (Defaults automatically to instance/finance.db)
DATABASE_URL=sqlite:///instance/finance.db

# Google Gemini API Key (Optional - FinBot works offline with local fallback if empty)
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# Port (Default: 5000)
PORT=5000
FLASK_ENV=development
```

> **Note:** FinBot will automatically use its internal rule-based advisor if `GEMINI_API_KEY` is left blank. You can add a free Gemini API key anytime from [Google AI Studio](https://aistudio.google.com/).

### 5. Seed Demo Data

Populate the database with realistic sample transactions, budgets, savings, and financial goals:

```bash
python seed_data.py
```

#### Demo User Credentials:
- **Email:** `demo@finbot.com`
- **Password:** `Demo@1234`

#### Secondary User (for isolation testing):
- **Email:** `student@finbot.com`
- **Password:** `Student@1234`

### 6. Run the Application

```bash
python run.py
```

Open your browser and navigate to: **http://localhost:5000** (or http://127.0.0.1:5000).

---

## 🧪 Running the Test Suite

Execute the full automated test suite with pytest:

```bash
pytest -v
```

All 14 test modules verify:
- Automatic database directory creation on fresh environments.
- User registration, login, logout, and password hashing.
- Route protection for unauthenticated requests.
- Complete CRUD operations on Income, Expense, Budget, Savings, and Goals.
- Financial analytics, category calculations, and health score algorithms.
- Strict multi-user record isolation (preventing unauthorized cross-user modifications).
- FinBot AI advisor execution and local offline fallback response generation.

---

## ☁️ Cloud & Production Deployment

### Database Path Guarantee
The application uses dynamic filesystem path resolution in `app/config.py` and `app/__init__.py`. On any platform (Windows, Linux, Docker, Render, Heroku), it creates the `instance/` folder using `os.makedirs(..., exist_ok=True)` before opening SQLite connections, preventing the common `"unable to open database file"` error.

### Running with Gunicorn (Production WSGI)

In production environments (such as Render or Linux VMs), run:

```bash
gunicorn run:app
```

With custom workers and binding:
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 4 run:app
```

### Deploying to Render.com
1. Create a new **Web Service** connected to your GitHub repository.
2. Set **Environment** to `Python 3`.
3. Set **Build Command**: `pip install -r requirements.txt && python seed_data.py`
4. Set **Start Command**: `gunicorn run:app`
5. Add Environment Variables:
   - `SECRET_KEY`: `<your-random-secret-key>`
   - `GEMINI_API_KEY`: `<your-gemini-api-key-or-blank>`
   - `FLASK_ENV`: `production`

---

## 🔒 Security Best Practices

- **Password Hashing:** Passwords are never stored in plaintext; Werkzeug PBKDF2 with SHA-256 is used.
- **Resource Ownership:** Every database query filters by `user_id == current_user.id`, and every update/delete operation checks record ownership returning `403 Forbidden` if breached.
- **Environment Isolation:** Sensitive credentials and database files (`*.db`, `.env`) are excluded in `.gitignore`.

---

## 📄 License
This project is open-source and built for educational and portfolio purposes.
