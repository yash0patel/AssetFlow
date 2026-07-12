# AssetFlow ERP

> Enterprise Asset Management Platform — React (Vite) + FastAPI + PostgreSQL + Redis

---

## Overview

**AssetFlow** is a full-stack enterprise asset management ERP built for organizations that need to track, allocate, and maintain their physical assets — from laptops and vehicles to conference rooms and office furniture.

### Problem it solves

Most organizations manage assets through spreadsheets, which breaks down quickly as the team grows. AssetFlow replaces that with a centralized, role-aware platform that:
- Tracks every asset from acquisition to disposal
- Manages who holds what and flags overdue returns automatically
- Routes maintenance requests through an approval workflow
- Prevents booking conflicts for shared resources
- Runs structured audit cycles with auto-generated discrepancy reports

### Target users

| Role | Typical usage |
|---|---|
| **Admin** | Organization setup, user management, full platform access |
| **Asset Manager** | Register assets, manage allocations, approve maintenance |
| **Department Head** | Approve transfers within their department, view dept-level reports |
| **Employee** | View own allocations, raise maintenance requests, book shared resources |

---

## Features

### Core capabilities

- **Asset Registration & Directory** — Auto-generated asset tags (AF-0001), serial numbers, acquisition details, condition tracking, QR codes, photo/document uploads
- **Allocation & Transfer** — Allocate assets to employees with conflict detection; blocked re-allocation shows current holder and offers a transfer request
- **Resource Booking** — Calendar view with real-time overlap validation; `10:00–11:00` is fine after a `9:00–10:00` booking
- **Maintenance Kanban** — Pending → Approved → Technician Assigned → In Progress → Resolved; asset status updates automatically
- **Asset Audit Cycles** — Assign auditors, mark each asset Verified / Missing / Damaged, auto-generate discrepancy reports, close and lock cycles
- **Reports & Analytics** — Utilization by department, maintenance frequency, idle assets, retirement alerts
- **Activity Logs & Notifications** — Every admin/manager/employee action is logged; role-specific notifications (overdue alerts, booking confirmations, etc.)
- **Organization Setup** — Department hierarchy, asset category management, employee directory with role assignment

### Auth features

- JWT access + refresh token flow
- Session-level revocation (not just token expiry)
- Backend-driven password reset via SMTP email
- Role-based route guards on both frontend and backend

---

## Tech Stack

### Frontend

| Tool | Version |
|---|---|
| React | 18.3.1 |
| Vite | 6.0.5 |
| React Router DOM | 6.28.0 |
| TanStack Query | 5.62.7 |
| Axios | 1.7.9 |
| React Hook Form + Zod | 7.54 / 3.23 |
| Recharts | 2.13.3 |
| CSS Modules | — |

### Backend

| Tool | Version |
|---|---|
| FastAPI | 0.115.5 |
| Uvicorn | 0.32.1 |
| SQLAlchemy 2 (async) | 2.0.36 |
| Alembic | 1.14.0 |
| Pydantic v2 | 2.10.3 |

### Database

| Tool | Version |
|---|---|
| PostgreSQL | 15+ |
| psycopg3 (binary) | 3.2.3 |

### Authentication

| Tool | Purpose |
|---|---|
| python-jose | JWT signing / verification |
| passlib + bcrypt | Password hashing |
| Redis sessions | Session revocation tracking |

### Deployment

- **Dev:** `uvicorn --reload` + `vite dev`
- **Production:** Gunicorn + Uvicorn workers (backend), static Vite build (frontend)

### Other Tools

| Tool | Purpose |
|---|---|
| Redis 7 | Cache, session storage, OTP, rate limiting |
| Alembic | Database schema migrations |
| black + isort + flake8 | Backend code quality |
| ESLint + Prettier | Frontend code quality |

---

## Project Structure

```
AssetFlow/
├── backend/                    # FastAPI application
│   ├── alembic/                # Migration environment + revision files
│   ├── app/
│   │   ├── api/v1/             # Route handlers (thin controllers, no business logic)
│   │   ├── core/               # Config, JWT, permissions, constants
│   │   ├── db/                 # Async engine, session factory, seed script
│   │   ├── middleware/         # Request logging, exception handlers
│   │   ├── models/             # SQLAlchemy ORM models (one file per domain)
│   │   ├── redis/              # Cache, session, OTP, rate-limiter helpers
│   │   ├── repositories/       # All database queries (data access layer)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic layer
│   │   ├── tests/              # Pytest test suite
│   │   ├── utils/              # Enums, email sender, QR generator, validators
│   │   └── main.py             # Application factory
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md               # Full backend developer docs
│
├── frontend/                   # React + Vite SPA
│   ├── src/
│   │   ├── components/         # Shared UI components (cards, tables, modals, etc.)
│   │   ├── context/            # AuthContext, ThemeContext, NotificationContext
│   │   ├── hooks/              # useAuth, useDebounce, useFetch, usePagination
│   │   ├── layouts/            # MainLayout (sidebar + topbar), AuthLayout
│   │   ├── pages/              # One folder per feature screen (10 screens)
│   │   ├── routes/             # createBrowserRouter config, PrivateRoute, RoleRoute
│   │   ├── services/           # Axios API service layer (one file per resource)
│   │   ├── styles/             # CSS custom properties (design tokens), global resets
│   │   └── utils/              # Helpers, formatters, constants
│   ├── .env.example
│   ├── package.json
│   └── README.md               # Full frontend developer docs
│
└── README.md                   # This file
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Browser (React SPA)             │
│         Vite • React Router • TanStack Query │
└─────────────────────┬───────────────────────┘
                      │ Axios REST  (Bearer JWT)
                      ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                 │
│                                             │
│  api/v1/ (Routers)                          │
│      ↓                                      │
│  services/ (Business Logic)                 │
│      ↓                          ↔  Redis    │
│  repositories/ (SQL Queries)    │  • Cache  │
│      ↓                          │  • OTP    │
│  SQLAlchemy async               │  • Rate   │
└──────────────┬──────────────────┘  limiting │
               │
               ▼
┌──────────────────────┐
│   PostgreSQL         │
│   (Primary DB)       │
└──────────────────────┘
```

**Request flow:** Router (validate input) → Service (business rules) → Repository (SQL) → PostgreSQL. Redis sits alongside the service layer for caching, sessions, and rate limiting.

---

## Prerequisites

| Tool | Min version |
|---|---|
| Python | 3.11 |
| Node.js | 18 LTS |
| PostgreSQL | 15 |
| Redis | 7 |

---

## Installation

### Clone repository

```bash
git clone https://github.com/yash0patel/AssetFlow.git
cd AssetFlow
```

### Backend setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env — at minimum set DATABASE_URL, REDIS_URL, SECRET_KEY
alembic upgrade head
```

> Full details — environment variables, migrations, seeding, deployment: **[backend/README.md](backend/README.md)**

### Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env — set VITE_API_BASE_URL if backend runs on a different port
```

> Full details — routing, state management, component guide, aliases: **[frontend/README.md](frontend/README.md)**

---

## Environment Variables

| File | Purpose |
|---|---|
| `backend/.env` | Database URL, Redis URL, JWT secret, SMTP credentials, log level |
| `frontend/.env` | API base URL, Axios timeout, app name, feature flags |

Copy from the provided templates:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

> See [backend/README.md → Environment Variables](backend/README.md) and [frontend/README.md → Environment Variables](frontend/README.md) for the full variable reference.

---

## Running the Project

Run both servers in separate terminals:

**Terminal 1 — Backend:**
```bash
cd backend
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## API Documentation

Interactive API docs are available in development mode at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Docs are disabled automatically when `DEBUG=False` (production).

The API is versioned under `/api/v1/`. Major resource groups:

| Prefix | Description |
|---|---|
| `/api/v1/auth` | Login, register, refresh, logout, password reset |
| `/api/v1/departments` | Department management |
| `/api/v1/asset-categories` | Category management |
| `/api/v1/employees` | Employee directory + role assignment |
| `/api/v1/assets` | Asset registration, search, lifecycle |
| `/api/v1/allocations` | Allocation, return, overdue tracking |
| `/api/v1/bookings` | Resource booking with overlap validation |
| `/api/v1/maintenance` | Maintenance request workflow |
| `/api/v1/audits` | Audit cycles + discrepancy reports |
| `/api/v1/dashboard` | KPI summary for the dashboard |
| `/api/v1/reports` | Analytics — utilization, idle assets, retirement |
| `/api/v1/notifications` | User notifications |
| `/api/v1/activity-logs` | Full audit trail |

---

## Screenshots

| Screen | Description |
|---|---|
| Dashboard | KPI cards, overdue return alert, quick actions |
| Organization Setup | Department tree, asset categories, employee directory |
| Asset Directory | Searchable asset list with lifecycle status badges |
| Allocation & Transfer | Conflict-aware allocation form + Transfer Request Kanban |
| Resource Booking | Calendar timeline with real-time overlap visualizer |
| Maintenance Board | 5-column Kanban: Pending → Resolved |
| Asset Audit | Verification checklist + auto-generated discrepancy report |
| Reports & Analytics | Bar + line charts, most-used / idle assets, retirement alerts |
| Notifications | Filtered activity log with read/unread toggles |

---

## Folder Structure

```
AssetFlow/
├── backend/
│   ├── alembic/                # Migration environment + version files
│   ├── app/
│   │   ├── api/v1/             # 13 route modules
│   │   ├── core/               # config.py, security.py, permissions.py, constants.py
│   │   ├── db/                 # database.py, session.py, base.py, seed.py, sequence.py
│   │   ├── middleware/         # exception_handler.py, logging.py, auth.py
│   │   ├── models/             # 15 ORM model files (one per domain)
│   │   ├── redis/              # client.py, cache.py, sessions.py, rate_limit.py
│   │   ├── repositories/       # Data access layer
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic (13 service files)
│   │   ├── tests/              # Pytest suite
│   │   ├── utils/              # email.py, enums.py, helpers.py, qr_generator.py
│   │   └── main.py
│   ├── .env / .env.example
│   ├── alembic.ini
│   ├── requirements.txt
│   └── README.md
│
└── frontend/
    ├── src/
    │   ├── components/         # cards/, charts/, common/, forms/, modals/, tables/, ui/
    │   ├── context/            # AuthContext, ThemeContext, NotificationContext
    │   ├── hooks/              # useAuth, useDebounce, useFetch, usePagination
    │   ├── layouts/            # MainLayout, AuthLayout
    │   ├── pages/              # 12 feature page directories (10 screens + auth + profile)
    │   ├── routes/             # AppRoutes, PrivateRoute, RoleRoute, routeConstants
    │   ├── services/           # api.js (Axios) + 10 resource service files
    │   ├── styles/             # theme.css (design tokens), globals.css
    │   └── utils/
    ├── .env / .env.example
    ├── vite.config.js
    ├── package.json
    └── README.md
```

---

## Contributors

| Name | Role |
|---|---|
| Yash Patel | Full-Stack Development |

---

## License

This project is proprietary. All rights reserved.

---

## Future Improvements

- [ ] **Celery / ARQ background jobs** — scheduled overdue-return flagging, audit reminders, automated reports
- [ ] **WebSocket notifications** — real-time push alerts instead of polling
- [ ] **Mobile app** — React Native companion for field teams to scan QR codes and update asset status on the go
- [ ] **Advanced RBAC** — attribute-based access control (ABAC) for fine-grained permission policies
- [ ] **Asset depreciation tracking** — tie acquisition cost to accounting schedules for net book value reports
- [ ] **Bulk import** — CSV/Excel import for mass asset registration during initial rollout
- [ ] **Full test coverage** — unit tests for all service layer functions, integration tests for all API endpoints
- [ ] **Docker Compose** — single-command local setup for the entire stack (API + DB + Redis + frontend)

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Migrations Guide](https://alembic.sqlalchemy.org/en/latest/)
- [TanStack Query Docs](https://tanstack.com/query/latest)
- [React Router v6 Docs](https://reactrouter.com/)
- [Pydantic v2 Docs](https://docs.pydantic.dev/)
- [React Hook Form Docs](https://react-hook-form.com/)
- [Recharts Docs](https://recharts.org/)
