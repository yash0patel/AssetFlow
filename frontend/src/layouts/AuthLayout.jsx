/** layouts/AuthLayout.jsx — Wraps public auth pages (login, register, etc.) */
import { Outlet } from "react-router-dom";

export default function AuthLayout() {
  return (
    <div className="auth-layout">
      <Outlet />
    </div>
  );
}
