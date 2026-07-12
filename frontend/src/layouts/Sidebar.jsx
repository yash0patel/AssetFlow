/**
 * layouts/Sidebar.jsx
 * ───────────────────
 * Main navigation sidebar.
 */

import { NavLink } from "react-router-dom";
import { useAuth } from "@hooks/useAuth";
import { ROUTES } from "@routes/routeConstants";
import styles from "./main-layout.module.css";

export default function Sidebar() {
  const { user, logout } = useAuth();

  const navItems = [
    { label: "Dashboard", path: ROUTES.DASHBOARD },
    // Temporarily linking Organization setup to DEPARTMENTS route for screen 3
    { label: "Organization setup", path: ROUTES.DEPARTMENTS },
    { label: "Assets", path: ROUTES.ASSETS },
    { label: "Allocation & Transfer", path: ROUTES.ALLOCATIONS },
    { label: "Resource Booking", path: ROUTES.BOOKINGS },
    { label: "Maintenance", path: ROUTES.MAINTENANCE },
    { label: "Audit", path: ROUTES.AUDITS },
    { label: "Reports", path: ROUTES.REPORTS },
    { label: "Notifications", path: ROUTES.NOTIFICATIONS },
  ];

  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>AssetFlow</div>
      
      <nav className={styles.nav}>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `${styles.navItem} ${isActive ? styles.navItemActive : ""}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className={styles.userSection}>
        <div className={styles.userInfo}>
          <span className={styles.userName}>{user?.name || "User"}</span>
          <span className={styles.userRole}>{user?.role || "Employee"}</span>
        </div>
        <button className={styles.logoutBtn} onClick={logout}>
          Logout
        </button>
      </div>
    </aside>
  );
}
