/**
 * pages/dashboard/Dashboard.jsx
 * ────────────────────────────
 * Dashboard providing a real-time operational snapshot.
 * Uses mock data based on the backend data models.
 */

import { useNavigate } from "react-router-dom";
import { ROUTES } from "@routes/routeConstants";
import styles from "./dashboard.module.css";

// ── Mock Data ──────────────────────────────────────────────────────────────────
const MOCK_KPIS = [
  { label: "Available", value: 128 },
  { label: "Allocated", value: 76 },
  { label: "Under Maintenance", value: 4 }, // Aligned with asset_status 'Under Maintenance'
  { label: "Active Bookings", value: 9 },
  { label: "Pending Transfers", value: 3 },
  { label: "Upcoming returns", value: 12 },
];

const MOCK_OVERDUE_COUNT = 3;

const MOCK_ACTIVITIES = [
  "Laptop AF-0114 - allocated to Priya shah - IT dept",
  "Room B2 - booking confirmed - 2:00 to 3:00 PM",
  "Projector AF-0062 - maintenance resolved",
];

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      {/* ── Today's Overview Section ────────────────────────────────────────── */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Today's Overview</h2>

        {/* KPI Grid */}
        <div className={styles.kpiGrid}>
          {MOCK_KPIS.map((kpi, idx) => (
            <div key={idx} className={styles.kpiCard}>
              <span className={styles.kpiLabel}>{kpi.label}</span>
              <span className={styles.kpiValue}>{kpi.value}</span>
            </div>
          ))}
        </div>

        {/* Overdue Banner */}
        {MOCK_OVERDUE_COUNT > 0 && (
          <div className={styles.overdueBanner}>
            {MOCK_OVERDUE_COUNT} assets overdue for return - flagged for follow-up
          </div>
        )}

        {/* Quick Actions */}
        <div className={styles.actionsRow}>
          <button
            className={`${styles.actionBtn} ${styles.primaryAction}`}
            onClick={() => navigate(ROUTES.ASSET_REGISTER)}
          >
            + register asset
          </button>
          <button
            className={styles.actionBtn}
            onClick={() => navigate(ROUTES.BOOKINGS)}
          >
            Book resource
          </button>
          <button
            className={styles.actionBtn}
            onClick={() => navigate(ROUTES.MAINTENANCE)}
          >
            Raise requests
          </button>
        </div>
      </section>

      {/* ── Recent Activity Section ─────────────────────────────────────────── */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Recent Activity</h2>
        <div className={styles.activityList}>
          {MOCK_ACTIVITIES.map((activity, idx) => (
            <div key={idx} className={styles.activityItem}>
              {activity}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
