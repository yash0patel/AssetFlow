/**
 * pages/reports/Reports.jsx
 * ─────────────────────────
 * Screen 9: Reports & Analytics Screen.
 */

import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import reportService from "@services/report.service";
import styles from "./reports.module.css";

export default function Reports() {
  const [utilizationData, setUtilizationData] = useState([]);
  const [maintenanceData, setMaintenanceData] = useState([]);
  const [assetsNearRetirement, setAssetsNearRetirement] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadReports() {
      try {
        const [utilData, maintData, retirementData] = await Promise.all([
          reportService.getDepartmentAllocationSummary(),
          reportService.getMaintenanceFrequency(),
          reportService.getAssetsNearRetirement(),
        ]);
        setUtilizationData(utilData);
        setMaintenanceData(maintData);
        setAssetsNearRetirement(retirementData);
      } catch (err) {
        console.error("Error loading reports data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadReports();
  }, []);

  const handleExport = () => {
    toast.success("Report export started (mock). Check your downloads.");
  };

  if (loading) {
    return <div className={styles.container}>Loading reports & analytics...</div>;
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.pageTitle}>Reports & Analytics</h1>

      {/* ── Top Half: Charts ─────────────────────────────────────────────── */}
      <div className={styles.chartsGrid}>
        <div className={styles.chartCard} style={{ backgroundColor: "#1e3a5f" }}>
          <span className={styles.cardTitle} style={{ color: "#fff" }}>Allocations by Department</span>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={utilizationData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip 
                  cursor={{ fill: "rgba(255,255,255,0.1)" }}
                  contentStyle={{ backgroundColor: "#202020", border: "none", borderRadius: "6px", color: "#fff" }}
                />
                <Bar dataKey="value" fill="#816729" radius={[4, 4, 0, 0]} barSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className={styles.chartCard} style={{ backgroundColor: "#1e3a5f" }}>
          <span className={styles.cardTitle} style={{ color: "#fff" }}>Maintenance Frequency</span>
          <div className={styles.chartWrapper}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={maintenanceData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="month" tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "rgba(255,255,255,0.7)", fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#202020", border: "none", borderRadius: "6px", color: "#fff" }}
                />
                <Line type="monotone" dataKey="count" stroke="#ff682c" strokeWidth={3} dot={{ r: 4, fill: "#ff682c" }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ── Middle Half: Lists ───────────────────────────────────────────── */}
      <div className={styles.listsGrid}>
        <div className={styles.listGroup}>
          <span className={styles.listTitle}>Most used assets (mock)</span>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Conference Room B2</span>: 34 bookings this month
          </div>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Dell XPS 15"</span>: 21 allocations this year
          </div>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Epson EB-X51</span>: 18 bookings
          </div>
        </div>

        <div className={styles.listGroup}>
          <span className={styles.listTitle}>Idle assets (mock)</span>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Cisco Switch 48-Port</span>: unused 60+ days
          </div>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Standing Desk</span>: unused 45 days
          </div>
        </div>
      </div>

      {/* ── Bottom Half: Due Maintenance ─────────────────────────────────── */}
      <div className={styles.bottomSection}>
        <div className={styles.listGroup}>
          <span className={styles.listTitle}>Assets Nearing Retirement</span>
          {assetsNearRetirement.length > 0 ? (
            assetsNearRetirement.map((asset) => (
              <div key={asset.id} className={styles.listItem}>
                <span className={styles.itemName}>{asset.asset_tag} - {asset.name}</span>: 
                retiring in {asset.days_remaining} days ({new Date(asset.expected_retirement_date).toLocaleDateString()})
              </div>
            ))
          ) : (
            <div className={styles.listItem} style={{ color: "var(--color-text-subtle)" }}>
              No assets nearing retirement within 90 days.
            </div>
          )}
        </div>

        <button className={styles.primaryBtn} onClick={handleExport}>
          Export report
        </button>
      </div>
    </div>
  );
}
