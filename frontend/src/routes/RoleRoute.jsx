/**
 * routes/RoleRoute.jsx
 * ─────────────────────
 * Renders children only when the authenticated user has the required role(s).
 * Shows a 403 page (or redirects to dashboard) for insufficient privileges.
 */

import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@hooks/useAuth";
import { ROUTES } from "./routeConstants";

/**
 * @param {string | string[]} allowedRoles — role(s) that may access the route
 *
 * Usage:
 *   <Route element={<RoleRoute allowedRoles={["admin", "super_admin"]} />}>
 *     <Route path="/admin" element={<AdminPanel />} />
 *   </Route>
 */
export default function RoleRoute({ allowedRoles = [] }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading…</div>;
  }

  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
  const hasAccess = user && roles.includes(user.role);

  return hasAccess ? (
    <Outlet />
  ) : (
    <Navigate to={ROUTES.DASHBOARD} replace />
  );
}
