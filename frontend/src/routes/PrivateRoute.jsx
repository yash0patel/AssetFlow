/**
 * routes/PrivateRoute.jsx
 * ────────────────────────
 * Renders children only when the user is authenticated.
 * Redirects to /login otherwise, preserving the intended destination.
 */

import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@hooks/useAuth";
import { ROUTES } from "./routeConstants";

/**
 * Wrap any route element with <PrivateRoute> to require authentication.
 *
 * Usage in AppRoutes.jsx:
 *   <Route element={<PrivateRoute />}>
 *     <Route path="/dashboard" element={<Dashboard />} />
 *   </Route>
 */
export default function PrivateRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    // TODO: replace with a full-screen loading spinner component
    return <div>Loading…</div>;
  }

  return isAuthenticated ? (
    <Outlet />
  ) : (
    <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />
  );
}
