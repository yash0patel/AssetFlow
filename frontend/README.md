# Frontend

## Overview

AssetFlow is an enterprise asset management ERP. This document covers everything needed to work on the **frontend** codebase only.

The frontend is a single-page application (SPA) built with React 18 + Vite. It communicates with a FastAPI backend over a REST API and uses mock data for screens that are not yet wired up.

---

## Tech Stack

| Layer | Library / Tool | Version |
|---|---|---|
| UI Framework | React | 18.3.1 |
| Build Tool | Vite | 6.0.5 |
| Language | JavaScript (ESM) | — |
| Routing | React Router DOM | 6.28.0 |
| Server State | TanStack Query (React Query) | 5.62.7 |
| HTTP Client | Axios | 1.7.9 |
| Forms | React Hook Form + Zod | 7.54 / 3.23 |
| Charts | Recharts | 2.13.3 |
| Toasts | React Hot Toast | 2.4.1 |
| Icons | React Icons | 5.4.0 |
| Dates | Day.js | 1.11.13 |
| Styling | CSS Modules + CSS Custom Properties | — |
| Linting | ESLint 9 | — |
| Formatting | Prettier | 3.4.2 |

---

## Folder Structure

```
frontend/
├── public/                     # Static assets served as-is
├── src/
│   ├── App.jsx                 # Root component — wires providers + router
│   ├── main.jsx                # Vite entry point
│   ├── index.css               # Root CSS import
│   │
│   ├── assets/                 # Images, SVGs, fonts
│   │
│   ├── components/             # Shared, reusable UI components
│   │   ├── cards/              # Stat cards, info cards
│   │   ├── charts/             # Chart wrappers
│   │   ├── common/             # Generic elements (Button, Badge, etc.)
│   │   ├── forms/              # Form field components
│   │   ├── modals/             # Modal overlays
│   │   ├── notifications/      # Notification widgets
│   │   ├── tables/             # Table components
│   │   └── ui/                 # Primitive UI elements
│   │
│   ├── context/                # React Context providers
│   │   ├── AuthContext.jsx     # Auth state + actions
│   │   ├── ThemeContext.jsx    # Light / dark theme toggle
│   │   └── NotificationContext.jsx
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.js
│   │   ├── useDebounce.js
│   │   ├── useFetch.js
│   │   └── usePagination.js
│   │
│   ├── layouts/                # Page shell layouts
│   │   ├── MainLayout.jsx      # Authenticated shell (sidebar + topbar)
│   │   └── AuthLayout.jsx      # Unauthenticated shell (centered card)
│   │
│   ├── pages/                  # Feature pages (one folder per route/feature)
│   │   ├── auth/               # Login, Register, ForgotPassword
│   │   ├── dashboard/          # Screen 2 — KPI cards + quick actions
│   │   ├── organization/       # Screen 3 — Departments, Categories, Employees
│   │   ├── assets/             # Screen 4 — Asset list, register, details
│   │   ├── allocation/         # Screen 5 — Allocation & Transfer Kanban
│   │   ├── bookings/           # Screen 6 — Resource Booking calendar
│   │   ├── maintenance/        # Screen 7 — Maintenance Kanban board
│   │   ├── audits/             # Screen 8 — Audit cycle + verification table
│   │   ├── reports/            # Screen 9 — Charts & analytics
│   │   ├── notifications/      # Screen 10 — Activity log & notifications
│   │   ├── activitylogs/       # Full admin audit trail
│   │   └── profile/            # User profile page
│   │
│   ├── routes/                 # Routing configuration
│   │   ├── AppRoutes.jsx       # createBrowserRouter tree
│   │   ├── PrivateRoute.jsx    # Redirect unauthenticated users
│   │   ├── RoleRoute.jsx       # Restrict routes by user role
│   │   └── routeConstants.js   # All ROUTES constants + buildRoute()
│   │
│   ├── services/               # API service layer (one file per resource)
│   │   ├── api.js              # Axios instance (interceptors, auth header)
│   │   ├── auth.service.js
│   │   ├── asset.service.js
│   │   ├── asset-category.service.js
│   │   ├── department.service.js
│   │   ├── employee.service.js
│   │   ├── booking.service.js
│   │   ├── maintenance.service.js
│   │   ├── audit.service.js
│   │   ├── notification.service.js
│   │   └── report.service.js
│   │
│   ├── styles/                 # Global CSS
│   │   ├── theme.css           # CSS custom properties (design tokens)
│   │   └── globals.css         # Base resets + utility classes
│   │
│   └── utils/                  # Pure helper functions
│
├── .env                        # Local env vars (git-ignored)
├── .env.example                # Template — copy to .env
├── .prettierrc                 # Prettier config
├── eslint.config.js            # ESLint flat config
├── vite.config.js              # Vite + path aliases + proxy
└── package.json
```

---

## Prerequisites

| Tool | Min version |
|---|---|
| Node.js | 18.x |
| npm | 9.x |

---

## Installation

```bash
# From the repo root
cd frontend
npm install
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Backend REST API base URL |
| `VITE_API_TIMEOUT` | `10000` | Axios timeout in milliseconds |
| `VITE_APP_NAME` | `AssetFlow` | App display name |
| `VITE_APP_VERSION` | `1.0.0` | App version |
| `VITE_ENABLE_DEVTOOLS` | `true` | Enables React Query Devtools in dev |

> All variables must be prefixed with `VITE_` to be exposed to the browser.

---

## Running Development Server

```bash
npm run dev
```

Opens at **http://localhost:5173**

API calls to `/api/*` are automatically proxied to `http://localhost:8001` (the FastAPI backend) via the Vite dev server proxy — no CORS issues.

---

## Build for Production

```bash
npm run build
```

Output goes to `dist/`. Bundles are split into separate chunks:
- `vendor` — React, React DOM, React Router
- `query` — TanStack Query
- `charts` — Recharts

Preview the production build locally:

```bash
npm run preview
```

---

## Available Scripts

| Script | Command | Description |
|---|---|---|
| Dev server | `npm run dev` | Starts Vite dev server with HMR |
| Build | `npm run build` | Production bundle to `dist/` |
| Preview | `npm run preview` | Serve the production `dist/` build |
| Lint | `npm run lint` | ESLint check (zero warnings policy) |
| Lint fix | `npm run lint:fix` | ESLint auto-fix |
| Format | `npm run format` | Prettier write over `src/**` |
| Format check | `npm run format:check` | Prettier check (CI-safe) |

---

## Routing

Routes are defined centrally in [`src/routes/AppRoutes.jsx`](src/routes/AppRoutes.jsx) using the React Router v6 `createBrowserRouter` API with **lazy loading** on every page.

All path strings live in [`src/routes/routeConstants.js`](src/routes/routeConstants.js) — always import from there; never hardcode strings.

### Public routes

| Path | Page |
|---|---|
| `/login` | Login |
| `/register` | Register |
| `/forgot-password` | Forgot Password |

### Protected routes (require auth)

| Path | Page | Role restriction |
|---|---|---|
| `/dashboard` | Dashboard | — |
| `/organization/departments` | Departments | Admin only |
| `/organization/employees` | Employees | Admin only |
| `/organization/asset-categories` | Asset Categories | Admin only |
| `/assets` | Asset List | — |
| `/assets/register` | Register Asset | — |
| `/assets/:id` | Asset Details | — |
| `/allocations` | Allocation & Transfer | — |
| `/bookings` | Resource Booking | — |
| `/maintenance` | Maintenance | — |
| `/audits` | Audits | — |
| `/reports` | Reports & Analytics | — |
| `/notifications` | Notifications | — |
| `/activity-logs` | Activity Logs | — |
| `/profile` | Profile | — |

- **`PrivateRoute`** — redirects unauthenticated users to `/login`.
- **`RoleRoute`** — renders a 403 / redirects if the user's role is not in `allowedRoles`.
- All unmatched paths (`*`) redirect to `/login`.

### Route helpers

```js
import { buildRoute, ROUTES } from "@routes/routeConstants";

// Build a dynamic route
buildRoute(ROUTES.ASSET_DETAILS, { id: "AF-001" }); // → "/assets/AF-001"
```

---

## State Management

| Category | Solution |
|---|---|
| Server / async state | TanStack Query (`useQuery`, `useMutation`) |
| Auth state | `AuthContext` (React Context) |
| Theme | `ThemeContext` (React Context) |
| Notifications | `NotificationContext` (React Context) |
| Local UI state | `useState` / `useReducer` (component-level) |
| Form state | React Hook Form |

### TanStack Query configuration

Configured once in `App.jsx`:

```js
new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,   // 5 min
      gcTime:    10 * 60 * 1000,  // 10 min
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

---

## API Integration

All HTTP calls go through the pre-configured Axios instance at [`src/services/api.js`](src/services/api.js):

- **Base URL** — `VITE_API_BASE_URL`
- **Auth header** — Bearer token auto-attached from `localStorage.access_token` via request interceptor
- **Token refresh** — 401 responses trigger a silent refresh attempt before redirecting to `/login`
- **Credentials** — `withCredentials: true` for cookie-based flows

Service files (`src/services/*.service.js`) wrap `api.js` for each resource. Example pattern:

```js
// services/asset.service.js
import api from "./api";

const assetService = {
  getAll: (params) => api.get("/assets", { params }).then(r => r.data),
  getById: (id)   => api.get(`/assets/${id}`).then(r => r.data),
  create:  (data) => api.post("/assets", data).then(r => r.data),
};

export default assetService;
```

### Mock data

Pages not yet connected to the backend use local mock files (e.g., `mockAssets.js`, `mockAllocations.js`). These are co-located inside their page folder under `src/pages/<feature>/`.

---

## UI Components

Reusable components live under `src/components/` organised by category:

| Folder | Contents |
|---|---|
| `cards/` | Stat cards, info cards for dashboard KPIs |
| `charts/` | Recharts wrappers (bar, line, pie) |
| `common/` | Generic elements: Badge, Button, Spinner |
| `forms/` | Form field wrappers with validation integration |
| `modals/` | Overlay modal shells |
| `notifications/` | Notification bell + dropdown |
| `tables/` | Table container, column headers, pagination |
| `ui/` | Primitives: Avatar, Divider, Tag |

---

## Styling Convention

The project uses **CSS Modules** scoped to each component/page, with global design tokens shared via CSS custom properties.

### Design tokens

Defined in [`src/styles/theme.css`](src/styles/theme.css) and available everywhere:

```css
/* Colors */
--color-primary-500: #6366F1;
--color-success:     #10B981;
--color-error:       #EF4444;
--color-bg:          #F8FAFC;
--color-surface:     #FFFFFF;
--color-text:        #0F172A;
--color-text-muted:  #64748B;

/* Spacing (4px base unit) */
--space-1: 0.25rem;   --space-4: 1rem;
--space-2: 0.5rem;    --space-6: 1.5rem;
--space-3: 0.75rem;   --space-8: 2rem;

/* Border radius */
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-full: 9999px;

/* Typography */
--font-sans: "Inter", system-ui, sans-serif;
--font-mono: "JetBrains Mono", monospace;

/* Shadows */
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
```

Dark theme overrides are applied via `[data-theme="dark"]` on the `<html>` element (toggled by `ThemeContext`).

### Writing styles

```jsx
// MyComponent.jsx
import styles from "./my-component.module.css";

export default function MyComponent() {
  return <div className={styles.container}>...</div>;
}
```

```css
/* my-component.module.css */
.container {
  padding: var(--space-6);
  background-color: var(--color-surface);
  border-radius: var(--radius-lg);
}
```

**Rules:**
- Never use inline styles except for dynamic computed values (e.g., pixel-perfect timeline positioning).
- Never use global class names — always CSS Modules.
- Always consume design tokens (`var(--...)`) — never hardcode hex colors or pixel values.

---

## Assets

Static assets (images, SVGs) live in `src/assets/`. Import them directly in JSX:

```js
import logo from "@assets/logo.svg";
```

Files placed in `public/` are served at the root path without hashing (e.g., `public/favicon.ico` → `/favicon.ico`).

---

## Path Aliases

Vite is configured with the following import aliases, so you never need relative `../../` hell:

| Alias | Resolves to |
|---|---|
| `@` | `src/` |
| `@components` | `src/components/` |
| `@pages` | `src/pages/` |
| `@hooks` | `src/hooks/` |
| `@services` | `src/services/` |
| `@context` | `src/context/` |
| `@utils` | `src/utils/` |
| `@routes` | `src/routes/` |
| `@layouts` | `src/layouts/` |
| `@assets` | `src/assets/` |
| `@styles` | `src/styles/` |

```js
// Good
import { useAuth } from "@hooks/useAuth";

// Avoid
import { useAuth } from "../../hooks/useAuth";
```

---

## Best Practices

- **One feature per folder** — keep page, CSS module, and mock data together.
- **Services over inline fetch** — all API calls go through `src/services/`, never raw `axios` in components.
- **TanStack Query for server state** — avoid `useEffect` + `useState` for data fetching.
- **React Hook Form + Zod** for all forms — co-locate schemas alongside the form component.
- **Early returns** — prefer guard clauses over deeply nested conditionals.
- **No hardcoded route strings** — always use `ROUTES` constants.
- **Meaningful names** — follow the naming convention: `camelCase` for functions/variables, `PascalCase` for components, `kebab-case` for files/folders.
- **Remove mock data before going live** — mock files (`mock*.js`) are clearly named and isolated.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Port 5173 already in use | `vite.config.js` has `strictPort: true` — kill the occupying process or change the port |
| API calls return 404 | Check `VITE_API_BASE_URL` in `.env` — it must match the backend port |
| API calls return CORS errors | Make sure the Vite proxy is active (dev only). In production, configure CORS on the backend |
| Blank page after build | Check browser console for dynamic import errors; ensure `dist/` is served from the correct base path |
| ESLint max-warnings exceeded | Run `npm run lint:fix` to auto-fix; remaining issues must be manually resolved |
| Font not loading | Check network tab — Google Fonts requires an internet connection in dev |

---

## Useful Commands

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Production build
npm run build

# Preview production build locally
npm run preview

# Auto-fix lint errors
npm run lint:fix

# Format all source files
npm run format

# Check formatting (used in CI)
npm run format:check
```
