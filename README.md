# AssetFlow ERP

> Enterprise Asset Management Platform — React (Vite) + FastAPI + PostgreSQL + Redis

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Backend setup](#2-backend-setup)
  - [3. Frontend setup](#3-frontend-setup)
- [Running the application](#running-the-application)
- [PostgreSQL setup](#postgresql-setup)
- [Redis setup](#redis-setup)
- [Alembic — database migrations](#alembic--database-migrations)
- [Environment variables](#environment-variables)
- [Folder structure](#folder-structure)
- [Code quality](#code-quality)

---

## Tech Stack

| Layer     | Technology                                  |
|-----------|---------------------------------------------|
| Frontend  | React 18, Vite 6, React Router v6           |
| Backend   | FastAPI, Uvicorn, Pydantic v2               |
| ORM       | SQLAlchemy 2.x (async)                      |
| Migrations| Alembic                                     |
| Database  | PostgreSQL 16+                              |
| Cache     | Redis 7+                                    |
| Auth      | JWT (python-jose) + bcrypt (passlib)        |

---

## Prerequisites

| Tool        | Minimum Version |
|-------------|-----------------|
| Python      | 3.12            |
| Node.js     | 22 LTS          |
| PostgreSQL  | 16              |
| Redis       | 7               |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/assetflow.git
cd assetflow
```

---

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and fill in values
cp .env.example .env
```

> **Edit `backend/.env`** — at minimum set `DATABASE_URL`, `REDIS_URL`, and `SECRET_KEY`.

---

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
```

> **Edit `frontend/.env`** — set `VITE_API_BASE_URL` if your backend runs on a non-default port.

---

## Running the application

### Backend

```bash
cd backend

# Activate venv first
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/Mac

uvicorn app.main:app --reload
```

API available at: **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**  
Health check: **http://localhost:8000/health**

### Frontend

```bash
cd frontend
npm run dev
```

App available at: **http://localhost:5173**

---

## PostgreSQL setup

1. Install PostgreSQL 16+ from https://www.postgresql.org/download/
2. Create the database:

```sql
CREATE DATABASE assetflow_db;
CREATE USER assetflow_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE assetflow_db TO assetflow_user;
```

3. Update `DATABASE_URL` in `backend/.env`:

```
DATABASE_URL=postgresql+psycopg://assetflow_user:yourpassword@localhost:5432/assetflow_db
```

Recommended GUI clients: **pgAdmin 4**, **DBeaver**

---

## Redis setup

### Windows

Install **Memurai Community** (Redis-compatible for Windows):  
https://www.memurai.com/get-memurai

Or use **WSL 2** with native Redis:
```bash
sudo apt install redis-server
sudo service redis-server start
```

### macOS / Linux

```bash
# macOS
brew install redis && brew services start redis

# Ubuntu / Debian
sudo apt install redis-server && sudo systemctl enable --now redis
```

Update `REDIS_URL` in `backend/.env`:
```
REDIS_URL=redis://localhost:6379/0
```

Recommended GUI: **RedisInsight** — https://redis.com/redis-enterprise/redis-insight/

---

## Alembic — database migrations

All commands run from the `backend/` directory with the venv activated.

```bash
# Generate a new migration after adding/changing models
alembic revision --autogenerate -m "describe the change"

# Apply all pending migrations
alembic upgrade head

# Roll back the last migration
alembic downgrade -1

# View migration history
alembic history --verbose

# View current applied revision
alembic current
```

> **Important:** Before running `autogenerate`, make sure your model file is imported in `app/db/base.py`.

---

## Environment variables

### Backend (`backend/.env`)

| Variable                     | Description                              | Default                          |
|------------------------------|------------------------------------------|----------------------------------|
| `APP_NAME`                   | Application name                         | `AssetFlow`                      |
| `ENVIRONMENT`                | `development` / `staging` / `production` | `development`                    |
| `DEBUG`                      | Enable SQL echo and debug docs           | `True`                           |
| `DATABASE_URL`               | PostgreSQL async DSN                     | —                                |
| `REDIS_URL`                  | Redis connection URL                     | `redis://localhost:6379/0`       |
| `SECRET_KEY`                 | JWT signing key                          | *(must be changed)*              |
| `ALGORITHM`                  | JWT algorithm                            | `HS256`                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Access token lifetime (minutes)          | `30`                             |
| `REFRESH_TOKEN_EXPIRE_DAYS`  | Refresh token lifetime (days)            | `7`                              |
| `FRONTEND_URL`               | Allowed CORS origin                      | `http://localhost:5173`          |
| `LOG_LEVEL`                  | Logging verbosity                        | `INFO`                           |

### Frontend (`frontend/.env`)

| Variable              | Description             | Default                              |
|-----------------------|-------------------------|--------------------------------------|
| `VITE_API_BASE_URL`   | FastAPI base URL        | `http://localhost:8000/api/v1`       |
| `VITE_API_TIMEOUT`    | Axios timeout (ms)      | `10000`                              |
| `VITE_APP_NAME`       | App display name        | `AssetFlow`                          |
| `VITE_ENABLE_DEVTOOLS`| Show React Query devtools| `true`                              |

---

## Folder structure

```
AssetFlow/
├── backend/
│   ├── alembic/             # Migration scripts
│   ├── app/
│   │   ├── api/v1/          # Route handlers (thin controllers)
│   │   ├── core/            # Config, security, permissions, constants
│   │   ├── db/              # Engine, session, base, seed
│   │   ├── middleware/      # Logging, auth, exception handlers
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── redis/           # Client, cache, sessions, rate limiter
│   │   ├── repositories/    # Database query layer
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic layer
│   │   ├── tests/           # Test suite
│   │   ├── utils/           # Enums, helpers, validators, QR generator
│   │   └── main.py          # FastAPI application factory
│   ├── .env                 # Local environment (git-ignored)
│   ├── .env.example         # Environment variable template
│   ├── requirements.txt     # Python dependencies
│   └── alembic.ini          # Alembic configuration
│
└── frontend/
    ├── public/              # Static assets
    ├── src/
    │   ├── assets/          # Images, icons, fonts
    │   ├── components/      # Reusable UI components
    │   ├── context/         # React context providers
    │   ├── hooks/           # Custom React hooks
    │   ├── layouts/         # Page layout components
    │   ├── pages/           # Feature pages (one folder per module)
    │   ├── routes/          # Router config, guards, constants
    │   ├── services/        # Axios API service functions
    │   ├── styles/          # Global CSS and design tokens
    │   └── utils/           # Constants, formatters, validators, helpers
    ├── .env                 # Local environment (git-ignored)
    ├── .env.example         # Environment variable template
    ├── package.json
    └── vite.config.js
```

---

## Code quality

### Backend

```bash
# Format with Black
black app/

# Sort imports
isort app/

# Lint with flake8
flake8 app/
```

### Frontend

```bash
# Lint with ESLint
npm run lint

# Auto-fix lint issues
npm run lint:fix

# Format with Prettier
npm run format

# Check formatting
npm run format:check
```

---

## Architecture overview

```
Frontend (React + Vite)
        ↕ Axios (REST)
Backend (FastAPI)
    ↓ Route Handlers (thin)
    ↓ Services (business logic)
    ↓ Repositories (SQL queries)
    ↓ PostgreSQL (via SQLAlchemy async)

Redis (alongside Service layer)
  • Dashboard KPI caching
  • OTP / session tokens
  • Rate limiting
  • Master data caching
```
