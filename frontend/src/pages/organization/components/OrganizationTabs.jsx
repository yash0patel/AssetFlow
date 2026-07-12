/**
 * pages/organization/components/OrganizationTabs.jsx
 * ──────────────────────────────────────────────────
 * Reusable tab navigation for the Organization Setup screen.
 */

import { NavLink } from "react-router-dom";
import { ROUTES } from "@routes/routeConstants";
import styles from "../organization.module.css";

export default function OrganizationTabs({ onAddClick, addLabel = "+ Add" }) {
  const tabs = [
    { label: "Departments", path: ROUTES.DEPARTMENTS },
    { label: "Categories", path: ROUTES.ASSET_CATEGORIES },
    { label: "Employee", path: ROUTES.EMPLOYEES },
  ];

  return (
    <div className={styles.tabsRow}>
      {tabs.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          className={({ isActive }) =>
            `${styles.tabBtn} ${isActive ? styles.tabActive : ""}`
          }
        >
          {tab.label}
        </NavLink>
      ))}

      <button className={styles.addBtn} onClick={onAddClick}>
        {addLabel}
      </button>
    </div>
  );
}
