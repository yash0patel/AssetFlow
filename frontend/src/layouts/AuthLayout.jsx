/**
 * layouts/AuthLayout.jsx
 * ───────────────────────
 * Full-page wrapper for public auth screens (Login, Register, ForgotPassword).
 * Renders children via <Outlet /> from React Router.
 */

import { Outlet } from "react-router-dom";

export default function AuthLayout() {
  return <Outlet />;
}
