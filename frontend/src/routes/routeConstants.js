/**
 * routes/routeConstants.js
 * ─────────────────────────
 * Central definition of all application route paths.
 * Import these constants everywhere instead of hardcoding strings.
 */

export const ROUTES = {
  // ── Public ────────────────────────────────────────────────────────────────
  LOGIN: "/login",
  REGISTER: "/register",
  FORGOT_PASSWORD: "/forgot-password",

  // ── Protected ─────────────────────────────────────────────────────────────
  DASHBOARD: "/dashboard",

  // Organization
  DEPARTMENTS: "/organization/departments",
  EMPLOYEES: "/organization/employees",
  ASSET_CATEGORIES: "/organization/asset-categories",

  // Assets
  ASSETS: "/assets",
  ASSET_DETAILS: "/assets/:id",
  ASSET_REGISTER: "/assets/register",

  // Allocation
  ALLOCATIONS: "/allocations",

  // Bookings
  BOOKINGS: "/bookings",

  // Maintenance
  MAINTENANCE: "/maintenance",

  // Audits
  AUDITS: "/audits",

  // Reports
  REPORTS: "/reports",

  // Notifications
  NOTIFICATIONS: "/notifications",

  // Activity Logs
  ACTIVITY_LOGS: "/activity-logs",

  // Profile
  PROFILE: "/profile",
};

/**
 * Helper to build a dynamic route (replaces :param placeholders).
 *
 * @example
 *   buildRoute(ROUTES.ASSET_DETAILS, { id: "AF-001" })
 *   // → "/assets/AF-001"
 */
export function buildRoute(template, params = {}) {
  return Object.entries(params).reduce(
    (path, [key, value]) => path.replace(`:${key}`, value),
    template
  );
}
