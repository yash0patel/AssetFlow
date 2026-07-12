/**
 * pages/dashboard/Dashboard.jsx
 * ────────────────────────────
 * Dashboard providing a real-time operational snapshot.
 * Uses real data from the backend API.
 */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ROUTES } from "@routes/routeConstants";
import dashboardService from "@services/dashboard.service";
import styles from "./dashboard.module.css";

export default function Dashboard() {
  const navigate = useNavigate();
  const [kpis, setKpis] = useState(null);
  const [overdueCount, setOverdueCount] = useState(0);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [kpiData, overdueData, activityData] = await Promise.all([
          dashboardService.getKpis(),
          dashboardService.getOverdueAllocations(),
          dashboardService.getRecentActivity(),
        ]);
        setKpis(kpiData);
        setOverdueCount(kpiData.overdue_returns || overdueData.length);
        setActivities(activityData.map(act => `${act.actor} - ${act.action} - ${act.entity_type} (${act.description})`));
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return <div className={styles.container}>Loading dashboard...</div>;
  }

  const kpiList = [
    { label: "Available", value: kpis?.assets_available || 0 },
    { label: "Allocated", value: kpis?.assets_allocated || 0 },
    { label: "Under Maintenance", value: kpis?.assets_under_maintenance || 0 },
    { label: "Active Bookings", value: kpis?.active_bookings || 0 },
    { label: "Pending Transfers", value: kpis?.pending_transfers || 0 },
    { label: "Upcoming returns", value: kpis?.upcoming_returns || 0 },
  ];

  return (
    <div className={styles.container}>
      {/* ── Today's Overview Section ────────────────────────────────────────── */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Today's Overview</h2>

        {/* KPI Grid */}
        <div className={styles.kpiGrid}>
          {kpiList.map((kpi, idx) => (
            <div key={idx} className={styles.kpiCard}>
              <span className={styles.kpiLabel}>{kpi.label}</span>
              <span className={styles.kpiValue}>{kpi.value}</span>
            </div>
          ))}
        </div>

        {/* Overdue Banner */}
        {overdueCount > 0 && (
          <div className={styles.overdueBanner}>
            {overdueCount} assets overdue for return - flagged for follow-up
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
          {activities.length > 0 ? (
            activities.map((activity, idx) => (
              <div key={idx} className={styles.activityItem}>
                {activity}
              </div>
            ))
          ) : (
            <div className={styles.activityItem}>No recent activities recorded.</div>
          )}
        </div>
      </section>
    </div>
  );
}
