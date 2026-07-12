/**
 * pages/assets/AssetDetails.jsx
 * ─────────────────────────────
 * Screen 4C: Per-asset detail view with allocation & maintenance history.
 */

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ROUTES } from "@routes/routeConstants";
import assetService from "@services/asset.service";
import allocationService from "@services/allocation.service";
import maintenanceService from "@services/maintenance.service";
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

  const [asset, setAsset] = useState(null);
  const [allocations, setAllocations] = useState([]);
  const [maintenance, setMaintenance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDetails() {
      setLoading(true);
      try {
        const [assetData, allocData, maintData] = await Promise.all([
          assetService.getAsset(id),
          allocationService.listAllocations({ asset_id: id }),
          maintenanceService.listMaintenanceRequests({ asset_id: id }),
        ]);
        setAsset(assetData);
        setAllocations(allocData.items || []);
        setMaintenance(maintData.items || []);
      } catch (err) {
        console.error("Error loading asset details:", err);
      } finally {
        setLoading(false);
      }
    }
    loadDetails();
  }, [id]);

  if (loading) {
    return <div className={styles.container}>Loading asset details...</div>;
  }

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
            <span className={styles.detailItemValue}>{asset.category_name}</span>
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
            <span className={styles.detailItemValue}>{asset.location_name || "—"}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Department</span>
            <span className={styles.detailItemValue}>{asset.department_name || "—"}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Acquisition Date</span>
            <span className={styles.detailItemValue}>{asset.acquisition_date || "—"}</span>
          </div>
          <div className={styles.detailItem}>
            <span className={styles.detailItemLabel}>Acquisition Cost</span>
            <span className={styles.detailItemValue}>
              {asset.acquisition_cost
                ? `₹${Number(asset.acquisition_cost).toLocaleString("en-IN")}`
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
                <th>Target</th>
                <th>Allocation Date</th>
                <th>Expected Return</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {allocations.length > 0 ? (
                allocations.map((h, i) => (
                  <tr key={i}>
                    <td className={styles.assetName}>
                      {h.allocated_to_employee_name || h.allocated_to_department_name}
                    </td>
                    <td>{new Date(h.allocation_date).toLocaleDateString()}</td>
                    <td>{h.expected_return_date || "—"}</td>
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
              {maintenance.length > 0 ? (
                maintenance.map((h, i) => (
                  <tr key={i}>
                    <td>{new Date(h.created_at).toLocaleDateString()}</td>
                    <td className={styles.assetName}>{h.issue_description}</td>
                    <td>{h.technician_name || "—"}</td>
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
