# Backend

## Overview

AssetFlow is an enterprise asset management ERP. This document covers everything needed to work on the **backend** codebase only.

The backend is a fully async REST API built with FastAPI + SQLAlchemy 2 (asyncio) + PostgreSQL. It serves the React frontend and handles authentication, all business logic, and background infrastructure.

---

## Tech Stack

| Layer | Library / Tool | Version |
|---|---|---|
| Web Framework | FastAPI | 0.115.5 |
| ASGI Server | Uvicorn (with `standard` extras) | 0.32.1 |
| ORM | SQLAlchemy 2 (async) | 2.0.36 |
| Migrations | Alembic | 1.14.0 |
| DB Driver | psycopg3 (binary) | 3.2.3 |
| Validation | Pydantic v2 + pydantic-settings | 2.10.3 / 2.6.1 |
| Auth | python-jose (JWT) + passlib + bcrypt | 3.3.0 / 1.7.4 / 4.2.1 |
| Cache / Sessions | redis-py | 5.2.1 |
| File Uploads | python-multipart + Pillow | 0.0.20 / 11.1.0 |
| HTTP Client | httpx | 0.28.1 |
| Linting | flake8 | 7.1.1 |
| Formatting | black + isort | 24.10.0 / 5.13.2 |

---

## Folder Structure

```
backend/
├── alembic/                    # Alembic migration environment
│   ├── env.py                  # Migration runner (async-aware)
│   ├── script.py.mako          # Migration template
│   └── versions/               # Generated migration files
│
├── app/
│   ├── main.py                 # Application factory (create_application)
│   │
│   ├── api/                    # Route layer (thin controllers only)
│   │   ├── deps.py             # Shared FastAPI dependencies (auth, DB session)
│   │   └── v1/                 # All v1 route modules
│   │       ├── auth.py
│   │       ├── departments.py
│   │       ├── asset_categories.py
│   │       ├── employees.py
│   │       ├── assets.py
│   │       ├── allocations.py
│   │       ├── bookings.py
│   │       ├── maintenance.py
│   │       ├── audits.py
│   │       ├── dashboard.py
│   │       ├── notifications.py
│   │       ├── reports.py
│   │       └── activity_logs.py
│   │
│   ├── core/                   # Infrastructure config — no business logic
│   │   ├── config.py           # pydantic-settings Settings class
│   │   ├── constants.py        # API prefix, pagination, cache TTLs, rate limits
│   │   ├── permissions.py      # UserRole enum + ROLE_HIERARCHY
│   │   └── security.py         # JWT helpers + bcrypt password utils
│   │
│   ├── db/                     # Database layer
│   │   ├── base.py             # DeclarativeBase for all models
│   │   ├── database.py         # Async engine + AsyncSessionLocal factory
│   │   ├── session.py          # `get_db` FastAPI dependency
│   │   ├── sequence.py         # Auto-incrementing tag sequences (e.g. AF-0001)
│   │   └── seed.py             # Dev seed script
│   │
│   ├── middleware/
│   │   ├── auth.py             # Auth middleware stub
│   │   ├── exception_handler.py# Global HTTP / validation / unhandled exception handlers
│   │   └── logging.py          # RequestLoggingMiddleware (method, path, status, ms)
│   │
│   ├── models/                 # SQLAlchemy ORM models (one file per domain)
│   │   ├── user.py             # User, UserProfile, Role, Permission, UserRole, RolePermission
│   │   ├── department.py       # Department, AssetCategory, AssetCategoryAttribute
│   │   ├── employee.py         # Employee
│   │   ├── asset.py            # Asset, AssetLocation, AssetStatusHistory
│   │   ├── allocation.py       # AssetAllocation
│   │   ├── transfer.py         # AssetTransferRequest
│   │   ├── booking.py          # ResourceBooking
│   │   ├── maintenance.py      # MaintenanceRequest, MaintenanceTechnician, MaintenanceStatusHistory
│   │   ├── audit.py            # AuditCycle, AuditCycleAuditor, AuditCycleItem, AuditDiscrepancyReport
│   │   ├── notification.py     # Notification
│   │   ├── activity_log.py     # ActivityLog
│   │   ├── analytics.py        # Analytics + aggregation models
│   │   └── shared.py           # EntityCodeSequence (tag generation)
│   │
│   ├── redis/
│   │   ├── client.py           # Redis async client singleton
│   │   ├── cache.py            # cache_set / cache_get / cache_delete helpers
│   │   ├── sessions.py         # Session and OTP storage helpers
│   │   └── rate_limit.py       # Sliding-window rate limiter
│   │
│   ├── repositories/           # Data access layer — all DB queries live here
│   │
│   ├── schemas/                # Pydantic v2 request/response schemas (per domain)
│   │
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py
│   │   ├── department_service.py
│   │   ├── asset_category_service.py
│   │   ├── employee_service.py
│   │   ├── asset_service.py
│   │   ├── allocation_service.py
│   │   ├── booking_service.py
│   │   ├── maintenance_service.py
│   │   ├── audit_service.py
│   │   ├── dashboard_service.py
│   │   ├── activity_service.py
│   │   ├── notification_service.py
│   │   └── report_service.py
│   │
│   ├── tests/                  # Pytest test suite
│   │
│   └── utils/                  # Pure helpers (no DI)
│       ├── email.py            # SMTP email sender (async via anyio)
│       ├── enums.py            # Shared Enum types for models/schemas/services
│       ├── helpers.py          # Generic helper functions
│       ├── qr_generator.py     # QR code generation for asset tags
│       └── validators.py       # Custom Pydantic validators
│
├── .env                        # Local environment config (git-ignored)
├── .env.example                # Template — copy to .env
├── .flake8                     # Flake8 config
├── alembic.ini                 # Alembic entrypoint
├── pyproject.toml              # Tool config (black, isort)
├── requirements.txt            # Pinned dependencies
└── run.py                      # Convenience entry point
```

---

## Project Architecture

The backend follows a strict **layered architecture**:

```
Request → Router (api/v1/) → Service (services/) → Repository (repositories/) → DB
                                         ↕
                                    Redis (cache/)
```

| Layer | Responsibility |
|---|---|
| **Router** | Parse request, call service, return response — no business logic |
| **Service** | All business rules, validations, and orchestration |
| **Repository** | All database queries — no business logic |
| **Schema** | Pydantic models for input validation and response serialisation |
| **Model** | SQLAlchemy ORM table definitions |
| **Redis** | Cache, sessions, OTP, rate limiting |

---

## Database Design

PostgreSQL is the primary database. Key domains and their main tables:

| Domain | Tables |
|---|---|
| Users & Auth | `users`, `user_profiles`, `roles`, `permissions`, `user_roles`, `role_permissions` |
| Organization | `departments`, `asset_categories`, `asset_category_attributes` |
| Employees | `employees` |
| Assets | `assets`, `asset_locations`, `asset_status_history` |
| Allocation | `asset_allocations`, `asset_transfer_requests` |
| Bookings | `resource_bookings` |
| Maintenance | `maintenance_requests`, `maintenance_technicians`, `maintenance_status_history` |
| Audit | `audit_cycles`, `audit_cycle_auditors`, `audit_cycle_items`, `audit_discrepancy_reports` |
| Notifications | `notifications` |
| Activity | `activity_logs` |
| Sequences | `entity_code_sequences` (generates AF-0001 style asset tags) |

**Key Enums** (`app/utils/enums.py`):

| Enum | Values |
|---|---|
| `AssetStatus` | available, allocated, under_maintenance, retired, lost, disposed |
| `AssetCondition` | new, good, fair, poor, damaged |
| `AllocationStatus` | active, returned, overdue |
| `BookingStatus` | pending, confirmed, cancelled, completed |
| `MaintenanceStatus` | scheduled, in_progress, completed, cancelled |
| `AuditStatus` | pending, in_progress, completed |
| `ActivityAction` | create, update, delete, login, logout, allocate, return, transfer |

---

## Authentication

- **Method:** JWT Bearer tokens (HS256)
- **Password hashing:** bcrypt via `passlib`
- **Access token:** 30 min expiry (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Refresh token:** 7 day expiry (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)
- **Session validation:** Every authenticated request validates the access token hash against an active session record in the database — revocation is supported
- **Password Reset:** Backend-driven SMTP email via `app/utils/email.py` (anyio thread executor)

### Token flow

```
POST /api/v1/auth/login
  → Returns { access_token, refresh_token, token_type }

All protected routes:
  Authorization: Bearer <access_token>

POST /api/v1/auth/refresh
  → Validates refresh_token → returns new access_token

POST /api/v1/auth/logout
  → Revokes current session
```

### Auth dependency (`app/api/deps.py`)

```python
# Inject into any protected route handler:
current_user: User = Depends(get_current_user)
```

`get_current_user` validates the bearer token, checks the DB session record, and verifies the user's account is `Active`.

---

## Authorization

Roles and hierarchy are defined in `app/core/permissions.py`:

```
employee < department_head < asset_manager < admin
```

| Role | Typical Access |
|---|---|
| `admin` | Full access — org setup, user management, all features |
| `asset_manager` | Asset lifecycle, allocation, maintenance approvals, reports |
| `department_head` | Department-scoped assets, approve transfers for their dept |
| `employee` | Self-service — view own allocations, raise requests, book resources |

Role-based route protection is enforced at the router level using `RoleRoute` on the frontend and via custom dependencies on the backend.

---

## API Structure

All API routes are versioned under `/api/v1/`. Interactive docs available at `/docs` (dev only).

| Prefix | Router file | Tag |
|---|---|---|
| `/api/v1/auth` | `v1/auth.py` | Auth |
| `/api/v1/departments` | `v1/departments.py` | Departments |
| `/api/v1/asset-categories` | `v1/asset_categories.py` | Asset Categories |
| `/api/v1/employees` | `v1/employees.py` | Employees |
| `/api/v1/assets` | `v1/assets.py` | Assets |
| `/api/v1/allocations` | `v1/allocations.py` | Allocations |
| `/api/v1/bookings` | `v1/bookings.py` | Bookings |
| `/api/v1/maintenance` | `v1/maintenance.py` | Maintenance |
| `/api/v1/audits` | `v1/audits.py` | Audits |
| `/api/v1/dashboard` | `v1/dashboard.py` | Dashboard |
| `/api/v1/notifications` | `v1/notifications.py` | Notifications |
| `/api/v1/reports` | `v1/reports.py` | Reports |
| `/api/v1/activity-logs` | `v1/activity_logs.py` | Activity Logs |
| `/health` | `main.py` | Health |

### Response format conventions

- **Success (list):** `{ data: [...], total: n, page: n, size: n }`
- **Success (single):** `{ data: {...} }` or direct Pydantic schema
- **Error:** `{ detail: "message" }` with appropriate HTTP status code
- **Pagination defaults:** page=1, size=20, max=100

---

## Environment Variables

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `AssetFlow` | Application name |
| `APP_VERSION` | `1.0.0` | API version |
| `ENVIRONMENT` | `development` | `development` \| `staging` \| `production` |
| `DEBUG` | `True` | Enables `/docs`, `/redoc`, SQL logging |
| `BACKEND_HOST` | `0.0.0.0` | Uvicorn bind host |
| `BACKEND_PORT` | `8000` | Uvicorn port |
| `BACKEND_URL` | `http://localhost:8000` | Public backend URL (used in CORS) |
| `FRONTEND_URL` | `http://localhost:5173` | Frontend origin (added to CORS allow-list) |
| `DATABASE_URL` | `postgresql+psycopg://postgres:root@localhost:5432/assetflow_db` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `REDIS_PASSWORD` | _(empty)_ | Redis password (leave empty if none) |
| `SECRET_KEY` | _(change this!)_ | JWT signing secret |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server host |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USER` | _(your email)_ | SMTP login username |
| `SMTP_PASSWORD` | _(app password)_ | SMTP login password / app password |
| `EMAILS_FROM_EMAIL` | _(your email)_ | Sender email address |
| `EMAILS_FROM_NAME` | `AssetFlow` | Sender display name |
| `LOG_LEVEL` | `INFO` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` |
| `MAX_UPLOAD_SIZE_MB` | `10` | Max file upload size |
| `UPLOAD_DIR` | `uploads` | Directory for uploaded files |

> **Production:** Set `DEBUG=False` — this disables `/docs`, `/redoc`, and `/openapi.json`. Always replace `SECRET_KEY` with a cryptographically random value.

---

## Installation

### Prerequisites

| Tool | Min version |
|---|---|
| Python | 3.11+ |
| PostgreSQL | 15+ |
| Redis | 7+ |

### Steps

```bash
# From the repo root
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Virtual Environment

```bash
# Create
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Deactivate
deactivate
```

---

## Database Setup

1. Create a PostgreSQL database:

```sql
CREATE DATABASE assetflow_db;
```

2. Set the `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql+psycopg://postgres:<password>@localhost:5432/assetflow_db
```

---

## Migrations

Alembic is configured with async support in `alembic/env.py`.

```bash
# Apply all pending migrations (create/update schema)
alembic upgrade head

# Create a new migration after changing a model
alembic revision --autogenerate -m "describe your change"

# Roll back the last migration
alembic downgrade -1

# Check current applied revision
alembic current

# View migration history
alembic history --verbose
```

> Always review the auto-generated migration file before applying to production.

---

## Seeding

The seed script wipes all existing data and repopulates realistic sample data for every module (roles, users, departments, assets, allocations, bookings, etc.).

```bash
# From the backend/ directory with .venv active
python -m app.db.seed
```

**What gets seeded:**
- Roles: `admin`, `asset_manager`, `department_head`, `employee`
- Sample users for each role
- Departments and asset categories
- Sample assets with status history
- Sample allocations, bookings, and maintenance requests

> **Warning:** This script deletes all existing data first. Never run against a production database.

---

## Running Server

```bash
# Development (with hot reload)
uvicorn app.main:app --reload

# Specific host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Using the convenience script
python run.py
```

Accessible at:
- API: `http://localhost:8000/api/v1/`
- Interactive docs: `http://localhost:8000/docs` (dev only)
- ReDoc: `http://localhost:8000/redoc` (dev only)
- Health check: `http://localhost:8000/health`

---

## API Endpoints

### Auth (`/api/v1/auth`)

| Method | Path | Description |
|---|---|---|
| POST | `/login` | Login — returns access + refresh tokens |
| POST | `/register` | Register a new user |
| POST | `/refresh` | Refresh access token |
| POST | `/logout` | Revoke session |
| POST | `/forgot-password` | Send password reset email |
| POST | `/reset-password` | Reset password with token |

### Departments (`/api/v1/departments`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List all departments |
| POST | `/` | Create department |
| GET | `/{id}` | Get department detail |
| PUT | `/{id}` | Update department |
| DELETE | `/{id}` | Deactivate department |

### Asset Categories (`/api/v1/asset-categories`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List categories |
| POST | `/` | Create category |
| PUT | `/{id}` | Update category |
| DELETE | `/{id}` | Delete category |

### Employees (`/api/v1/employees`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List employees (filterable by dept/role/status) |
| POST | `/` | Create employee |
| GET | `/{id}` | Get employee |
| PUT | `/{id}` | Update employee |
| PATCH | `/{id}/role` | Promote/change role |

### Assets (`/api/v1/assets`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List assets (filterable by tag/category/status/dept) |
| POST | `/` | Register asset |
| GET | `/{id}` | Asset detail + history |
| PUT | `/{id}` | Update asset |
| GET | `/{id}/history` | Allocation + maintenance history |

### Allocations (`/api/v1/allocations`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List allocations |
| POST | `/` | Allocate asset |
| POST | `/{id}/return` | Mark returned |
| GET | `/overdue` | List overdue allocations |

### Transfers (`/api/v1/allocations/transfers`)

| Method | Path | Description |
|---|---|---|
| POST | `/` | Raise transfer request |
| PUT | `/{id}/approve` | Approve transfer |
| PUT | `/{id}/reject` | Reject transfer |

### Bookings (`/api/v1/bookings`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List bookings (filterable by resource/date) |
| POST | `/` | Create booking (overlap-validated) |
| PUT | `/{id}/cancel` | Cancel booking |

### Maintenance (`/api/v1/maintenance`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List maintenance requests |
| POST | `/` | Raise request |
| PUT | `/{id}/approve` | Approve (moves asset to Under Maintenance) |
| PUT | `/{id}/reject` | Reject |
| PUT | `/{id}/assign` | Assign technician |
| PUT | `/{id}/resolve` | Resolve (reverts asset to Available) |

### Audits (`/api/v1/audits`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List audit cycles |
| POST | `/` | Create audit cycle |
| PUT | `/{id}/verify-item` | Mark asset verified/missing/damaged |
| PUT | `/{id}/close` | Close cycle + generate discrepancy report |

### Dashboard (`/api/v1/dashboard`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | KPI summary (assets available, allocated, overdue, etc.) |

### Reports (`/api/v1/reports`)

| Method | Path | Description |
|---|---|---|
| GET | `/utilization` | Asset utilization by department |
| GET | `/maintenance-frequency` | Maintenance count over time |
| GET | `/idle-assets` | Assets unused beyond threshold |
| GET | `/retirement` | Assets nearing retirement / due for service |

### Notifications (`/api/v1/notifications`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | List user notifications |
| PUT | `/{id}/read` | Mark as read |

### Activity Logs (`/api/v1/activity-logs`)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Full audit trail (paginated, filterable) |

---

## Background Jobs

The backend does not use a dedicated task queue (Celery/ARQ) yet. Async background work is done via:

- **`anyio.to_thread.run_sync`** — used for blocking SMTP sends in `app/utils/email.py`
- **FastAPI `BackgroundTasks`** — used for post-response tasks like logging and sending notifications

Future background job candidates: overdue-return flagging cron, audit reminders, scheduled report generation.

---

## Redis

Redis is used for three purposes:

| Purpose | Module | Key Prefix |
|---|---|---|
| **Cache-Aside** | `redis/cache.py` | `cache:` |
| **Session / OTP storage** | `redis/sessions.py` | `session:` / `otp:` |
| **Rate limiting** | `redis/rate_limit.py` | `rate_limit:` |

### TTL reference

| Constant | Value |
|---|---|
| `CACHE_TTL_SHORT` | 60 s (1 min) |
| `CACHE_TTL_MEDIUM` | 300 s (5 min) |
| `CACHE_TTL_LONG` | 1800 s (30 min) |
| `CACHE_TTL_DAY` | 86400 s (24 h) |

### Cache invalidation

Services call `cache_delete` or `cache_delete_pattern` after mutating operations. Example: updating a department deletes `departments:*`.

> Redis is **optional at startup** — the server logs a warning and continues if Redis is unavailable. Only cache-dependent features degrade.

---

## Logging

Logging is configured in `main.py` using Python's `logging.config.dictConfig`.

- **Format:** `YYYY-MM-DD HH:MM:SS | LEVEL    | logger | message`
- **Output:** stdout (console)
- **Level:** controlled by `LOG_LEVEL` env var (default `INFO`)
- **SQL queries:** logged at `DEBUG` level when `DEBUG=True`
- **Request logging:** `RequestLoggingMiddleware` logs method, path, status code, and response time for every request
- **SQLAlchemy engine:** suppressed at `WARNING` in production to avoid noisy query logs

---

## Testing

Test files live in `app/tests/`. The suite is minimal at this stage.

```bash
# Run all tests
pytest

# With verbose output
pytest -v

# Run a specific file
pytest app/tests/test_auth.py
```

> The test directory currently contains only `__init__.py`. This is the designated location for the full test suite to be built by the development team.

---

## Deployment Notes

- Set `DEBUG=False` in production — disables all OpenAPI/Swagger endpoints
- Set `ENVIRONMENT=production`
- Replace `SECRET_KEY` with a cryptographically random value (e.g. `openssl rand -hex 32`)
- Configure `FRONTEND_URL` to the real production frontend origin for proper CORS
- Run database migrations before starting the server: `alembic upgrade head`
- Use a process manager (e.g. Gunicorn + Uvicorn workers, or a Docker container) instead of bare `uvicorn`

```bash
# Production-grade startup (Gunicorn with Uvicorn workers)
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --bind 0.0.0.0:8000
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `connection refused` on DB | Ensure PostgreSQL is running and `DATABASE_URL` matches your setup |
| `connection refused` on Redis | Ensure Redis is running. The server will start without it but caching will fail |
| `alembic: can't locate revision` | Run `alembic upgrade head` to apply all migrations |
| `422 Unprocessable Entity` | Check request body matches the Pydantic schema — inspect `/docs` |
| `401 Unauthorized` | Token is expired or session was revoked — re-login to get a fresh token |
| `403 Forbidden` | User's role is insufficient for that endpoint |
| SMTP email not sending | Verify `SMTP_USER`, `SMTP_PASSWORD` (use Gmail App Password, not account password), and that `SMTP_PORT=587` |
| Windows `asyncio` errors | The app sets `WindowsSelectorEventLoopPolicy` automatically in `main.py` and `seed.py` |

---

## Useful Commands

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload

# Apply all migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "your migration description"

# Roll back last migration
alembic downgrade -1

# Seed the database (wipes and repopulates)
python -m app.db.seed

# Run tests
pytest

# Format code
black app/
isort app/

# Lint
flake8 app/

# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```
