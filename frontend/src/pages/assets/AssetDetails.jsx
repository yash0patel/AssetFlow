/**
 * pages/assets/AssetDetails.jsx
 * ─────────────────────────────
 * Screen 4C: Per-asset detail view with allocation & maintenance history.
 */

import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ROUTES } from "@routes/routeConstants";
import { MOCK_ASSETS } from "./mockAssets";
import styles from "./asset.module.css";

// ── Status badge colour mapping ────────────────────────────────────────────────
const STATUS_CLASS = {
  Available:           styles.badgeAvailable,
  Allocated:           styles.badgeAllocated,
  Reserved:            styles.badgeReserved,
  "Under Maintenance": styles.badgeMaintenance,
  Lost:                styles.badgeLost,
  Retired:             styles.badgeRetired,
  Disposed:            styles.badgeDisposed,
};

const HISTORY_TABS = ["Allocation History", "Maintenance History"];

export default function AssetDetails() {
  const { id }       = useParams();
  const navigate     = useNavigate();
  const [activeTab, setActiveTab] = useState(0);

  const asset = MOCK_ASSETS.find((a) => a.id === id);

  if (!asset) {
    return (
      <div className={styles.container}>
        <button className={styles.backBtn} onClick={() => navigate(ROUTES.ASSETS)}>← Back</button>
        <p style={{ marginTop: "var(--space-6)", color: "var(--color-text-muted)" }}>
          Asset not found.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* ── Back + Title ──────────────────────────────────────────────────── */}
      <div className={styles.detailHeader}>
        <div className={styles.detailMeta}>
          <button className={styles.backBtn} onClick={() => navigate(ROUTES.ASSETS)}>
            ← Back to Assets
          </button>
          <span className={styles.detailAssetTag}>{asset.asset_tag}</span>
          <h1 className={styles.detailTitle}>{asset.name}</h1>
        </div>
        <span className={`${styles.badge} ${STATUS_CLASS[asset.current_status] || ""}`}>
          {asset.current_status}
        </span>
      </div>

      {/* ── Key Details Card ──────────────────────────────────────────────── */}
      <div className={styles.formCard}>
        <div className={styles.detailGrid}>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Category</span>
            <span className={styles.detailItemValue}>{asset.category}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Condition</span>
            <span className={styles.detailItemValue}>{asset.condition}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Serial Number</span>
            <span className={styles.detailItemValue}>{asset.serial_number || "—"}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Location</span>
            <span className={styles.detailItemValue}>{asset.location}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Department</span>
            <span className={styles.detailItemValue}>{asset.department}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Acquisition Date</span>
            <span className={styles.detailItemValue}>{asset.acquisition_date || "—"}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Acquisition Cost</span>
            <span className={styles.detailItemValue}>
              {asset.acquisition_cost
                ? `₹${asset.acquisition_cost.toLocaleString("en-IN")}`
                : "—"}
            </span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Bookable</span>
            <span className={styles.detailItemValue}>{asset.is_bookable ? "Yes" : "No"}</span>
          </div>
          {asset.description && (
            <div className={styles.detailItem} style={{ gridColumn: "1 / -1" }}>
              <span className={styles.detailItemLabel}>Description</span>
              <span className={styles.detailItemValue}>{asset.description}</span>
            </div>
          )}
        </div>
      </div>

      {/* ── History Tabs ──────────────────────────────────────────────────── */}
      <div className={styles.tableContainer}>
        <div className={styles.historyTabs}>
          {HISTORY_TABS.map((tab, idx) => (
            <button
              key={tab}
              className={`${styles.historyTab} ${activeTab === idx ? styles.historyTabActive : ""}`}
              onClick={() => setActiveTab(idx)}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Allocation History */}
        {activeTab === 0 && (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Employee</th>
                <th>Allocation Date</th>
                <th>Expected Return</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {asset.allocation_history.length > 0 ? (
                asset.allocation_history.map((h, i) => (
                  <tr key={i}>
                    <td className={styles.assetName}>{h.employee}</td>
                    <td>{h.date}</td>
                    <td>{h.return_date || "—"}</td>
                    <td>
                      <span
                        className={`${styles.badge} ${
                          h.status === "Active"
                            ? styles.badgeAllocated
                            : styles.badgeAvailable
                        }`}
                      >
                        {h.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className={styles.emptyState}>
                    No allocation history.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        {/* Maintenance History */}
        {activeTab === 1 && (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Date</th>
                <th>Issue</th>
                <th>Technician</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {asset.maintenance_history.length > 0 ? (
                asset.maintenance_history.map((h, i) => (
                  <tr key={i}>
                    <td>{h.date}</td>
                    <td className={styles.assetName}>{h.issue}</td>
                    <td>{h.technician}</td>
                    <td>
                      <span
                        className={`${styles.badge} ${
                          h.status === "Resolved"
                            ? styles.badgeAvailable
                            : styles.badgeMaintenance
                        }`}
                      >
                        {h.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className={styles.emptyState}>
                    No maintenance history.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
