/**
 * pages/activitylogs/ActivityLogs.jsx
 * ──────────────────────────────────
 * Screen 10B: Premium Audit Trails & Activity Logs Directory.
 */

import { useEffect, useState } from "react";
import activityLogService from "@services/activity-log.service";
import styles from "./activity-logs.module.css";

const ACTION_OPTIONS = ["Create", "Update", "Delete", "Approve", "Reject", "Cancel", "Close", "Login", "Logout"];

export default function ActivityLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    async function loadLogs() {
      setLoading(true);
      try {
        const data = await activityLogService.listActivityLogs({
          action: action || undefined,
          page,
          page_size: 25,
        });
        setLogs(data.items || []);
        setTotalPages(data.pages || 1);
      } catch (err) {
        console.error("Error loading activity logs:", err);
      } finally {
        setLoading(false);
      }
    }
    loadLogs();
  }, [action, page]);

  const getActionBadgeClass = (act) => {
    if (act === "Create") return styles.badgeCreate;
    if (act === "Update") return styles.badgeUpdate;
    if (act === "Delete") return styles.badgeDelete;
    return styles.badgeOther;
  };

  return (
    <div className={styles.container}>
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>Audit Logs & History</h1>
      </div>

      {/* Filters */}
      <div className={styles.filtersRow}>
        <select 
          className={styles.select}
          value={action}
          onChange={(e) => {
            setAction(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Actions</option>
          {ACTION_OPTIONS.map(a => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>
      </div>

      {/* Logs Table */}
      <div className={styles.tableContainer}>
        {loading ? (
          <div style={{ padding: "var(--space-6)", textAlign: "center" }}>Loading audit trails...</div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Actor</th>
                <th>Role</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.length > 0 ? (
                logs.map((log) => (
                  <tr key={log.id}>
                    <td style={{ whiteSpace: "nowrap" }}>
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td style={{ fontWeight: 600 }}>{log.actor}</td>
                    <td>{log.actor_role || "—"}</td>
                    <td>
                      <span className={`${styles.actionBadge} ${getActionBadgeClass(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td>{log.entity_type}</td>
                    <td style={{ maxWidth: "300px", fontSize: "0.8125rem", color: "var(--color-text-subtle)" }}>
                      {log.new_value ? JSON.stringify(log.new_value) : "—"}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "var(--space-6)" }}>
                    No audit records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className={styles.pagination}>
          <button 
            className={styles.pageBtn} 
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Prev
          </button>
          <span style={{ alignSelf: "center", fontSize: "0.875rem" }}>Page {page} of {totalPages}</span>
          <button 
            className={styles.pageBtn} 
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
