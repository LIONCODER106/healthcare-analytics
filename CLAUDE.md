# CLAUDE.md — Healthcare Analytics Codebase Guide

## Project Overview

Home Healthcare Analytics is a **Streamlit** web application for home healthcare agencies. It processes visit records from Excel/CSV files, tracks client and employee activity, calculates service fees, and generates billing reports. The app supports manual data entry for paper-based records and stores everything in a relational database.

The codebase was originally Replit-only and was refactored to support multiple database backends and deployment targets.

---

## Tech Stack

- **Frontend/Framework**: Streamlit (single-page app with sidebar navigation)
- **Database ORM**: SQLAlchemy (supports MySQL, PostgreSQL, SQLite)
- **Data Processing**: Pandas, NumPy
- **Authentication**: bcrypt password hashing
- **File Formats Supported**: `.xlsx`, `.xlsm`, `.xls`, `.csv`
- **Python**: 3.9+ required (3.11 recommended)
- **Container**: Docker + docker-compose (optional)

---

## File Structure

```
healthcare-analytics/
├── app.py                    # Main Streamlit app — all UI pages and session state
├── config.py                 # Centralized configuration (database URLs, env vars)
├── database.py               # SQLAlchemy models + init_db(), get_db(), test_connection()
├── db_service.py             # DatabaseService class — all DB CRUD operations
├── data_processor.py         # DataProcessor — file cleaning and frequency analysis
├── fee_calculator.py         # FeeCalculator — rate management and billing calculations
├── data_storage.py           # DataStorage — JSON-based analysis history (last 50 records)
├── client_service_manager.py # ClientServiceManager — JSON-based client hour configs
├── utils.py                  # Pure utility functions (formatting, export, validation)
├── requirements.txt          # Python dependencies
├── setup.sh                  # Interactive setup script (venv, deps, DB selection)
├── Dockerfile                # Python 3.11-slim image, exposes port 8501
├── docker-compose.yml        # App + MySQL + phpMyAdmin stack
├── .env.example              # Template for environment variables
├── README.md                 # Deployment guide and quick start
├── DEPLOYMENT_GUIDE.md       # Platform-specific deployment instructions
├── DATA_CLEANING_GUIDE.md    # Data format specification for uploads
├── PROJECT_DOCUMENTATION.md  # Feature documentation
├── QUICKSTART.md             # 5-minute setup guide
└── CHANGES.md                # What changed vs. original Replit version
```

---

## Database Models (database.py)

| Model | Table | Purpose |
|---|---|---|
| `User` | `users` | Authentication; bcrypt-hashed passwords; `is_admin` flag |
| `ServiceType` | `service_types` | Service definitions (medical/non-medical, rate, billing method) |
| `Client` | `clients` | Client records (auto-created on first encounter) |
| `ClientServiceConfig` | `client_service_configs` | Per-client service hour/rate overrides |
| `PeriodOverride` | `period_overrides` | Temporary billing period adjustments |
| `ManualEntry` | `manual_entries` | Paper-record entries (client, caregiver, hours, date) |
| `ConfigHistory` | `config_history` | Audit trail for configuration changes |

### Default seed data (created by `init_db()`)
- **User**: username `Billingpro`, password `Guard2026!`, `is_admin=True`
- **Service Types**: Home Health - Nursing ($130/hr), Home Health - Basic ($41.45/hr), Home Health - Physical Therapy ($143/hr), Personal Care ($35/hr)

---

## Configuration (config.py)

All settings are read from environment variables (`.env` file via `python-dotenv`).

### Key environment variables

| Variable | Default | Description |
|---|---|---|
| `DB_TYPE` | `mysql` | `mysql`, `postgresql`, or `sqlite` |
| `MYSQL_HOST` | `localhost` | MySQL host |
| `MYSQL_PORT` | `3306` | MySQL port |
| `MYSQL_DATABASE` | `healthcare_db` | Database name |
| `MYSQL_USER` | `healthcare_user` | MySQL user |
| `MYSQL_PASSWORD` | *(required)* | MySQL password |
| `DATABASE_URL` | — | Full PostgreSQL URL (overrides individual vars) |
| `SQLITE_PATH` | `healthcare.db` | SQLite file path |
| `SECRET_KEY` | `change-this-in-production-2025` | App secret |
| `PORT` | `8501` | Streamlit port |
| `MAX_UPLOAD_SIZE_MB` | `200` | Max file upload size |
| `SESSION_TIMEOUT_MINUTES` | `120` | Session timeout |

`Config.get_database_url()` builds the SQLAlchemy connection string from these variables. `Config.validate_config()` returns `(is_valid, errors)` and warns if `SECRET_KEY` is still the default.

---

## Data Flow

### Upload & Analysis Flow
1. User uploads `.xlsx`/`.xlsm`/`.csv` file(s) on the **Data Analysis** page
2. `DataProcessor.clean_data(df)` filters rows where **column O == "verified"** (case-insensitive), strips whitespace from columns A, B, C
3. `DataProcessor.analyze_data(cleaned_df)` produces `value_counts()` DataFrames for columns A (client name), B (employee), C (service type)
4. Results stored in `st.session_state.current_analysis` and `st.session_state.cleaned_data`
5. `DataStorage.save_analysis()` persists summary to `analysis_history.json` (capped at 50 entries)

### Critical data contract — column mapping in uploaded files
| Column | Meaning |
|---|---|
| A | Client name |
| B | Employee/caregiver name |
| C | Service type |
| O | Verification status — **must contain "verified"** for row to be processed |

If columns are not literally named `A`/`B`/`C`/`O`, `DataProcessor` falls back to positional mapping (columns 0, 1, 2, 14).

### Billing Flow
1. `DatabaseService.get_all_service_types()` retrieves rates from DB
2. Combined electronic (from `cleaned_data`) + manual entries are merged into a single billing DataFrame
3. `FeeCalculator.calculate_fees(service_analysis)` multiplies visit counts by per-service rates
4. Client-specific overrides via `ClientServiceManager` or `ClientServiceConfig` in DB can override default rates

---

## App Pages (app.py navigation)

| Page | Description |
|---|---|
| Data Analysis | File upload (single/batch), data processing, top-10 tables |
| Reports | Service type breakdown, client billing matrix, employee performance, export |
| Billing | Comprehensive billing with electronic + manual data combined |
| Client Service Configuration | Per-client service hour configuration (uses `DatabaseService`) |
| Service Type Management | CRUD for service types via `DatabaseService` |
| Service Fee Configuration | Rate updates for service types |
| Manual Entry | Paper-record data entry saved to `ManualEntry` table |
| Historical Records | Past analysis runs from `DataStorage` |
| Export Data | CSV downloads for various reports |
| Animation Demo | UI showcase (dev/demo only) |

---

## Service Layer (db_service.py)

`DatabaseService` is the single interface for all database operations. It holds a single SQLAlchemy session (`self.db`) and exposes grouped methods:

- **Service types**: `get_all_service_types`, `create_service_type`, `update_service_type`, `delete_service_type` (soft-delete by default)
- **Clients**: `get_all_clients`, `create_client`, `get_or_create_client`
- **Client configs**: `get_client_configs`, `create_client_config` (upserts on duplicate)
- **Manual entries**: `create_manual_entry`, `get_all_manual_entries`, `delete_manual_entry`
- **Auth**: `authenticate_user` — opens a **fresh session per call** (does not use `self.db`) and expunges the user before closing

`DatabaseService` is instantiated once per Streamlit session and stored in `st.session_state.db_service`.

---

## Local JSON Storage

Two classes persist data to JSON files as a lightweight layer alongside the database:

| Class | Files | Purpose |
|---|---|---|
| `DataStorage` | `analysis_history.json` | History of processed file summaries (max 50) |
| `ClientServiceManager` | `client_service_hours.json`, `client_hours_history.json` | Legacy client hour configs and audit trail |

These JSON files are not authoritative for billing — the database (`client_service_configs`) is. `ClientServiceManager` exists for legacy compatibility.

`FeeCalculator` also reads/writes `service_rates.json` as a cache but the database is the source of truth for rates in the current version.

---

## Authentication

- Login is handled in `show_login_page()` in `app.py`
- `DatabaseService.authenticate_user(username, password)` queries the `User` model and calls `user.check_password()` (bcrypt)
- On success, `st.session_state.logged_in = True` and `st.session_state.current_user` holds `{username, role, is_admin, full_name}`
- All pages are gated: `if not st.session_state.logged_in: show_login_page(); st.stop()`
- Default credentials: **username** `Billingpro` / **password** `Guard2026!` — change immediately in production

---

## Development Setup

```bash
# 1. Run automated setup (interactive — asks which DB to use)
./setup.sh

# 2. Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DB credentials

# 3. Initialize the database
python -c "from database import init_db; init_db()"

# 4. Run the app
streamlit run app.py
# Opens at http://localhost:8501
```

### Quickest path (SQLite, no DB setup needed)
```bash
echo "DB_TYPE=sqlite" > .env
source venv/bin/activate && pip install -r requirements.txt
python -c "from database import init_db; init_db()"
streamlit run app.py
```

### Docker
```bash
docker-compose up          # Starts app + MySQL + phpMyAdmin
# App: http://localhost:8501
# phpMyAdmin: http://localhost:8080
```

---

## Testing & Debugging

There is **no automated test suite** in this codebase. Manual testing checklist:

1. `python database.py` — tests DB connection and prints config info
2. `python config.py` — prints current configuration and validates it
3. Upload a sample `.xlsx` file on the Data Analysis page
4. Verify row filtering (only "verified" rows in column O should appear)
5. Check billing totals match expected rate × visit count

**Common issues:**
- `Database connection failed`: run `python database.py` and check `.env` credentials
- `Module not found`: activate the virtualenv (`source venv/bin/activate`)
- `MYSQL_PASSWORD required`: SQLite is the easiest fallback (`DB_TYPE=sqlite` in `.env`)
- Empty analysis results: uploaded file may lack a column O with "verified" values

---

## Deployment

The app requires a **persistent process** (Streamlit uses WebSockets) — it cannot run on traditional cPanel shared hosting.

**Supported targets:**
- VPS (DigitalOcean, Linode, AWS EC2) — recommended
- Render.com / Streamlit Cloud / Heroku — free/cheap cloud options
- Docker container on any host
- cPanel only if it has "Setup Python App" feature (limited)

See `DEPLOYMENT_GUIDE.md` for platform-specific instructions.

### Production checklist
- [ ] Change `SECRET_KEY` in `.env`
- [ ] Change default `Billingpro` password after first login
- [ ] Use strong DB passwords
- [ ] Enable HTTPS/SSL
- [ ] Set up regular DB backups
- [ ] Set `DB_TYPE=mysql` or `DB_TYPE=postgresql` (not sqlite)

---

## Key Conventions

- **No test framework** — validate via manual UI testing and `python database.py`
- **Session state over globals** — all stateful objects (`db_service`, `fee_calculator`, `data_storage`, etc.) live in `st.session_state`
- **Soft deletes** — `ServiceType` and `Client` use `is_active=False` rather than hard deletes
- **Upsert pattern** — `create_client_config` updates an existing config if one already exists for that client+service pair
- **DataFrame column names** — uploaded files are normalized to `A`, `B`, `C`, `O` internally; never use positional index after `DataProcessor.clean_data()`
- **Currency** — always use `format_currency()` from `utils.py` for display; store as `float`
- **Dates** — stored as `datetime.utcnow()` in the DB; displayed as ISO strings in JSON files

---

## Branch & Git

- Development branch: `claude/claude-md-docs-c9zpks`
- Main branch: `main`
- Push with: `git push -u origin <branch-name>`
