# CLAUDE.md — Healthcare Analytics

This file provides guidance for AI assistants working in this codebase.

---

## Project Overview

A Streamlit-based web application for home healthcare agencies to manage visit data, calculate billing, and generate reports. Supports MySQL, PostgreSQL, and SQLite backends with Docker deployment.

**Tech Stack**: Python 3.9+, Streamlit 1.45.1, SQLAlchemy 2.0+, pandas, bcrypt

---

## Repository Structure

```
healthcare-analytics/
├── app.py                      # Main Streamlit app (UI, pages, session state)
├── config.py                   # Multi-database configuration via env vars
├── database.py                 # SQLAlchemy models + DB initialization
├── db_service.py               # Database CRUD service layer
├── data_processor.py           # File upload, data cleaning, analysis
├── fee_calculator.py           # Service rate management, billing calculations
├── client_service_manager.py   # Client configuration and period overrides
├── data_storage.py             # JSON-based historical analysis persistence
├── utils.py                    # Formatting, export, and utility functions
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-service orchestration (app + MySQL + phpMyAdmin)
└── setup.sh                    # Interactive setup script
```

---

## Architecture

### Data Flow
```
Streamlit UI (app.py)
    └── Session State Management
        └── Business Logic Services
            ├── DataProcessor        – file handling & cleaning
            ├── FeeCalculator        – billing engine
            ├── ClientServiceManager – configuration management
            ├── DataStorage          – historical persistence
            └── DatabaseService      – CRUD (db_service.py)
                └── SQLAlchemy ORM (database.py)
                    └── MySQL / PostgreSQL / SQLite
```

### Database Models (database.py)
| Model | Purpose |
|---|---|
| `User` | Authentication — bcrypt-hashed passwords, admin flag |
| `ServiceType` | Service definitions with rates and billing methods |
| `Client` | Client records (soft-delete via `is_active`) |
| `ClientServiceConfig` | Per-client service rates and schedules |
| `PeriodOverride` | Temporary service adjustments with date ranges |
| `ConfigHistory` | Audit trail for all changes (JSON diffs) |
| `ManualEntry` | Paper-based record entry |

### Default Credentials (seeded on first run)
- **Username**: `Billingpro`
- **Password**: `Guard2026!`

> Change immediately in production.

---

## Development Setup

### Quick Start (SQLite — no database required)
```bash
bash setup.sh          # Interactive setup
# OR manually:
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit as needed
streamlit run app.py
```

### Docker (recommended for full stack)
```bash
docker-compose up      # starts app + MySQL + phpMyAdmin
# App:        http://localhost:8501
# phpMyAdmin: http://localhost:8080
```

### Environment Variables (config.py)
| Variable | Purpose | Default |
|---|---|---|
| `DB_TYPE` | `mysql`, `postgresql`, or `sqlite` | `sqlite` |
| `MYSQL_HOST` | MySQL hostname | `localhost` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_DATABASE` | Database name | — |
| `MYSQL_USER` | MySQL user | — |
| `MYSQL_PASSWORD` | MySQL password | — |
| `DATABASE_URL` | Full PostgreSQL URL | — |
| `SQLITE_PATH` | Path to SQLite file | `./data/healthcare.db` |
| `SECRET_KEY` | App session secret | — |
| `PORT` | Streamlit port | `8501` |
| `MAX_UPLOAD_SIZE_MB` | File upload limit | `50` |
| `SESSION_TIMEOUT_MINUTES` | Auth session TTL | `60` |

---

## Key Conventions

### Code Style
- PEP 8: `lowercase_with_underscores` for functions and variables
- Business logic is organized in class-based modules (see service files)
- Type hints used throughout (Python 3.9+)
- SQLAlchemy parameterized queries only — never raw string interpolation in SQL

### UI Conventions (app.py)
- Custom neumorphic CSS design system applied globally
- Page routing is handled via Streamlit session state (`st.session_state`)
- All database calls go through `db_service.py`, not directly via models
- User authentication state lives in `st.session_state['user']`

### Database Conventions
- Soft deletes: set `is_active = False`, never hard-delete records
- All mutations should log to `ConfigHistory` with action `'create'`, `'update'`, or `'delete'`
- New models must be added to `database.py` and initialized in `init_db()`
- Default seed data belongs in the `seed_default_data()` function in `database.py`

### Data Processing (data_processor.py)
- Excel/CSV uploads are cleaned via fixed rules:
  1. Column O must equal `"verified"` (case-insensitive)
  2. Whitespace stripped from columns A, B, C
  3. Empty rows removed
- Modifying these rules affects all existing data pipelines — test carefully

### Billing Logic (fee_calculator.py)
- Two billing methods: `'hourly'` and `'unit'`
- Unit type is `'hour'` or `'15min'`
- Per-client custom rates in `ClientServiceConfig.custom_rate` override `ServiceType.default_rate`

---

## Testing

There is currently **no automated test suite**. Before making changes:

1. Test locally with SQLite (`DB_TYPE=sqlite`) first
2. Verify Docker stack works: `docker-compose up` and check all three services
3. Test the affected UI flow manually through the Streamlit interface
4. For database changes, test against SQLite, then MySQL

Adding tests (pytest) would be a valuable contribution — place them in `/tests`.

---

## Common Tasks

### Add a new service type
1. Seed it in `database.py → seed_default_data()`, or add via the UI admin panel
2. Ensure `billing_method` and `unit_type` are set correctly

### Add a new database column
1. Add the column to the SQLAlchemy model in `database.py`
2. Add `Column(...)` with a default so existing rows aren't broken
3. Run the app — `init_db()` calls `Base.metadata.create_all()` which adds new columns on SQLite but **not** on MySQL/PostgreSQL (no migration framework)
4. For production MySQL/PostgreSQL, write a manual `ALTER TABLE` migration

### Add a new UI page
1. Add a new section/function in `app.py`
2. Add navigation entry to the sidebar routing in `app.py`
3. Gate behind `st.session_state['user']` check if auth is required

### Update dependencies
```bash
pip install -r requirements.txt --upgrade
# Pin the new version in requirements.txt before committing
```

---

## Security Notes

- Passwords are hashed with **bcrypt** — never store plaintext
- All DB queries use SQLAlchemy ORM (parameterized) — no raw string SQL
- Credentials must come from environment variables, never hardcoded
- The `.env` file must never be committed (it is in `.gitignore`)
- Default credentials (`Billingpro` / `Guard2026!`) are for development only

---

## Deployment Options

| Method | Best For |
|---|---|
| Docker Compose | Self-hosted VPS, full stack |
| Streamlit Cloud | Free hosting, SQLite only |
| Render / Heroku | Cloud PaaS with managed database |
| VPS + systemd | Production with Nginx reverse proxy |
| cPanel | Limited — requires Python App support |

See `DEPLOYMENT_GUIDE.md` for step-by-step instructions.

---

## Files to Understand First

When starting work in this repo, read these files in order:

1. `config.py` — understand how database connections are configured
2. `database.py` — understand the data models
3. `db_service.py` — understand available CRUD operations
4. `app.py` — understand UI structure and session state (large file, skim first)
