/**
 * pages/reports/Reports.jsx
 * ─────────────────────────
 * Screen 9: Reports & Analytics Screen.
 */

import React from "react";
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
import styles from "./reports.module.css";

// Mock Data for Charts
const utilizationData = [
  { name: "Eng", value: 45 },
  { name: "HR", value: 60 },
  { name: "Sales", value: 40 },
  { name: "Ops", value: 55 },
  { name: "Mktg", value: 30 },
];

const maintenanceData = [
  { month: "Jan", count: 10 },
  { month: "Feb", count: 15 },
  { month: "Mar", count: 12 },
  { month: "Apr", count: 20 },
  { month: "May", count: 25 },
  { month: "Jun", count: 28 },
];

export default function Reports() {
  const handleExport = () => {
    toast.success("Report export started (mock). Check your downloads.");
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.pageTitle}>Reports & Analytics</h1>

      {/* ── Top Half: Charts ─────────────────────────────────────────────── */}
      <div className={styles.chartsGrid}>
        <div className={styles.chartCard} style={{ backgroundColor: "#1e3a5f" }}>
          <span className={styles.cardTitle} style={{ color: "#fff" }}>Utilization by department</span>
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
                {/* Brass color for bars as per brand guidelines warm accents */}
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
                {/* Ember Orange line as per brand guidelines */}
                <Line type="monotone" dataKey="count" stroke="#ff682c" strokeWidth={3} dot={{ r: 4, fill: "#ff682c" }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ── Middle Half: Lists ───────────────────────────────────────────── */}
      <div className={styles.listsGrid}>
        <div className={styles.listGroup}>
          <span className={styles.listTitle}>Most used assets</span>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Room B2</span>: 34 bookings this month
          </div>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Van AF-343</span>: 21 trips this month
          </div>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Projector AF-335</span>: 18 uses
          </div>
        </div>

        <div className={styles.listGroup}>
          <span className={styles.listTitle}>Idle assets</span>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Camera AF-0301</span>: unused 60+ days
          </div>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Chair AF-0410</span>: unused 45 days
          </div>
        </div>
      </div>

      {/* ── Bottom Half: Due Maintenance ─────────────────────────────────── */}
      <div className={styles.bottomSection}>
        <div className={styles.listGroup}>
          <span className={styles.listTitle}>Assets due for maintenance / nearing retirement</span>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Forklift AF-0087</span>: service due in 5 days
          </div>
          <div className={styles.listItem}>
            <span className={styles.itemName}>Laptop AF-0020</span>: 4 years old (nearing retirement)
          </div>
        </div>

        <button className={styles.primaryBtn} onClick={handleExport}>
          Export report
        </button>
      </div>
    </div>
  );
}
