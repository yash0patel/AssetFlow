/**
 * pages/assets/AssetList.jsx
 * ───────────────────────────
 * Screen 4A: Asset Directory with search, filter, and table.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ROUTES, buildRoute } from "@routes/routeConstants";
import {
  MOCK_ASSETS,
  MOCK_CATEGORIES,
  MOCK_STATUSES,
  MOCK_DEPARTMENTS,
} from "./mockAssets";
import styles from "./asset.module.css";

// ── Status badge colour mapping ────────────────────────────────────────────────
const STATUS_CLASS = {
  Available:         styles.badgeAvailable,
  Allocated:         styles.badgeAllocated,
  Reserved:          styles.badgeReserved,
  "Under Maintenance": styles.badgeMaintenance,
  Lost:              styles.badgeLost,
  Retired:           styles.badgeRetired,
  Disposed:          styles.badgeDisposed,
};

export default function AssetList() {
  const navigate = useNavigate();

  const [search, setSearch]         = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [filterStatus, setFilterStatus]     = useState("");
  const [filterDept, setFilterDept]         = useState("");

  // Filter assets based on search + dropdown filters
  const filtered = MOCK_ASSETS.filter((a) => {
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      a.asset_tag.toLowerCase().includes(q) ||
      a.name.toLowerCase().includes(q) ||
      (a.serial_number || "").toLowerCase().includes(q);

    const matchCat  = !filterCategory || a.category   === filterCategory;
    const matchStat = !filterStatus   || a.current_status === filterStatus;
    const matchDept = !filterDept     || a.department  === filterDept;

    return matchSearch && matchCat && matchStat && matchDept;
  });

  const openDetails = (id) =>
    navigate(buildRoute(ROUTES.ASSET_DETAILS, { id }));

  return (
    <div className={styles.container}>
      {/* ── Search + Register CTA ────────────────────────────────────────── */}
      <div className={styles.searchRow}>
        <div className={styles.searchWrapper}>
          <input
            className={styles.searchInput}
            type="text"
            placeholder="Search by tag, serial, or QR code…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <button
          className={styles.registerBtn}
          onClick={() => navigate(ROUTES.ASSET_REGISTER)}
        >
          + Register Asset
        </button>
      </div>

      {/* ── Filter Dropdowns ─────────────────────────────────────────────── */}
      <div className={styles.filterRow}>
        <select
          className={styles.filterSelect}
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          <option value="">Category</option>
          {MOCK_CATEGORIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <select
          className={styles.filterSelect}
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">Status</option>
          {MOCK_STATUSES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <select
          className={styles.filterSelect}
          value={filterDept}
          onChange={(e) => setFilterDept(e.target.value)}
        >
          <option value="">Department</option>
          {MOCK_DEPARTMENTS.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      {/* ── Assets Table ─────────────────────────────────────────────────── */}
      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Tag</th>
              <th>Name</th>
              <th>Category</th>
              <th>Status</th>
              <th>Location</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length > 0 ? (
              filtered.map((asset) => (
                <tr
                  key={asset.id}
                  className={styles.clickableRow}
                  onClick={() => openDetails(asset.id)}
                >
                  <td><span className={styles.assetTag}>{asset.asset_tag}</span></td>
                  <td><span className={styles.assetName}>{asset.name}</span></td>
                  <td>{asset.category}</td>
                  <td>
                    <span className={`${styles.badge} ${STATUS_CLASS[asset.current_status] || ""}`}>
                      {asset.current_status}
                    </span>
                  </td>
                  <td>{asset.location}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className={styles.emptyState}>
                  No assets match your search or filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
