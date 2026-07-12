/**
 * pages/assets/AssetList.jsx
 * ───────────────────────────
 * Screen 4A: Asset Directory with search, filter, and table.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ROUTES, buildRoute } from "@routes/routeConstants";
import assetService from "@services/asset.service";
import assetCategoryService from "@services/asset-category.service";
import departmentService from "@services/department.service";
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

const STATUS_OPTIONS = [
  "Available",
  "Allocated",
  "Reserved",
  "Under Maintenance",
  "Lost",
  "Retired",
  "Disposed",
];

export default function AssetList() {
  const navigate = useNavigate();

  const [assets, setAssets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);

  const [search, setSearch]         = useState("");
  const [filterCategory, setFilterCategory] = useState("");
  const [filterStatus, setFilterStatus]     = useState("");
  const [filterDept, setFilterDept]         = useState("");

  useEffect(() => {
    async function loadFilters() {
      try {
        const [catData, deptData] = await Promise.all([
          assetCategoryService.listCategories(),
          departmentService.listDepartments(),
        ]);
        setCategories(catData.items || catData);
        setDepartments(deptData.items || deptData);
      } catch (err) {
        console.error("Error loading dropdown filters:", err);
      }
    }
    loadFilters();
  }, []);

  useEffect(() => {
    async function loadAssets() {
      setLoading(true);
      try {
        const params = {
          search: search || undefined,
          category_id: filterCategory || undefined,
          status: filterStatus || undefined,
          department_id: filterDept || undefined,
          page_size: 100,
        };
        const data = await assetService.listAssets(params);
        setAssets(data.items || []);
      } catch (err) {
        console.error("Error loading assets:", err);
      } finally {
        setLoading(false);
      }
    }
    loadAssets();
  }, [search, filterCategory, filterStatus, filterDept]);

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
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        <select
          className={styles.filterSelect}
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">Status</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>

        <select
          className={styles.filterSelect}
          value={filterDept}
          onChange={(e) => setFilterDept(e.target.value)}
        >
          <option value="">Department</option>
          {departments.map((d) => (
            <option key={d.id} value={d.id}>{d.name}</option>
          ))}
        </select>
      </div>

      {/* ── Assets Table ─────────────────────────────────────────────────── */}
      <div className={styles.tableContainer}>
        {loading ? (
          <div className={styles.emptyState}>Loading assets...</div>
        ) : (
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
              {assets.length > 0 ? (
                assets.map((asset) => (
                  <tr
                    key={asset.id}
                    className={styles.clickableRow}
                    onClick={() => openDetails(asset.id)}
                  >
                    <td><span className={styles.assetTag}>{asset.asset_tag}</span></td>
                    <td><span className={styles.assetName}>{asset.name}</span></td>
                    <td>{asset.category_name}</td>
                    <td>
                      <span className={`${styles.badge} ${STATUS_CLASS[asset.current_status] || ""}`}>
                        {asset.current_status}
                      </span>
                    </td>
                    <td>{asset.location_name || "-"}</td>
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
        )}
      </div>
    </div>
  );
}
