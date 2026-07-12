/**
 * pages/audits/Audits.jsx
 * ───────────────────────
 * Screen 8: Asset Audit Screen.
 */

import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import auditService from "@services/audit.service";
import assetService from "@services/asset.service";
import departmentService from "@services/department.service";
import employeeService from "@services/employee.service";
import styles from "./audit.module.css";

export default function Audits() {
  const [cycle, setCycle] = useState(null);
  const [items, setItems] = useState([]);
  const [isCycleActive, setIsCycleActive] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Options for creation
  const [departments, setDepartments] = useState([]);
  const [locations, setLocations] = useState([]);
  const [employees, setEmployees] = useState([]);

  // State for new cycle modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newStartDate, setNewStartDate] = useState("");
  const [newEndDate, setNewEndDate] = useState("");
  const [scopeDept, setScopeDept] = useState("");
  const [scopeLoc, setScopeLoc] = useState("");
  const [selectedAuditors, setSelectedAuditors] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadActiveCycle = async () => {
    setLoading(true);
    try {
      const data = await auditService.listCycles({ status: "In Progress" });
      const active = data.items?.[0] || null;
      setCycle(active);
      setIsCycleActive(!!active);

      if (active) {
        const itemsData = await auditService.getCycleItems(active.id);
        setItems(itemsData);
      }
    } catch (err) {
      console.error("Error loading active audit cycle:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadFormOptions = async () => {
    try {
      const [deptData, locData, empData] = await Promise.all([
        departmentService.listDepartments(),
        assetService.listLocations(),
        employeeService.listEmployees(),
      ]);
      setDepartments(deptData.items || deptData);
      setLocations(locData);
      setEmployees(empData.items || empData);
    } catch (err) {
      console.error("Error loading form options for audits:", err);
    }
  };

  useEffect(() => {
    loadActiveCycle();
    loadFormOptions();
  }, []);

  const handleVerification = async (itemId, status) => {
    if (!isCycleActive || !cycle) return;
    
    try {
      await auditService.verifyItem(cycle.id, itemId, {
        verification_status: status,
        remarks: "Verified via Audit UI",
      });
      // Optimistic or simple refresh
      setItems(prev => prev.map(a => a.id === itemId ? { ...a, verification_status: status } : a));
      toast.success(`Asset marked as ${status}.`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to verify item.");
    }
  };

  const handleCloseCycle = async () => {
    if (!cycle) return;
    if (items.some(a => a.verification_status === "Pending")) {
      if (!window.confirm("Some assets are not yet verified. Close anyway?")) {
        return;
      }
    }
    
    try {
      await auditService.closeCycle(cycle.id);
      setIsCycleActive(false);
      setCycle(null);
      setItems([]);
      toast.success("Audit cycle closed successfully. Discrepancy report generated.");
      await loadActiveCycle();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to close cycle.");
    }
  };

  const handleCreateCycle = async (e) => {
    e.preventDefault();
    if (!newTitle.trim() || !newStartDate || !newEndDate) {
      toast.error("Please provide audit title, start, and end dates.");
      return;
    }
    
    setIsSubmitting(true);
    try {
      await auditService.createCycle({
        cycle_name: newTitle,
        start_date: newStartDate,
        end_date: newEndDate,
        scope_department_id: scopeDept || null,
        scope_location_id: scopeLoc || null,
        auditor_ids: selectedAuditors,
      });

      toast.success("New audit cycle started.");
      setIsModalOpen(false);
      
      // Reset form
      setNewTitle("");
      setNewStartDate("");
      setNewEndDate("");
      setScopeDept("");
      setScopeLoc("");
      setSelectedAuditors([]);

      await loadActiveCycle();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to start audit cycle.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const flaggedCount = items.filter(a => a.verification_status === "Missing" || a.verification_status === "Damaged").length;

  if (loading && !cycle) {
    return <div className={styles.container}>Loading audit data...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>Asset Audit</h1>
        {!isCycleActive && (
          <button className={styles.primaryBtn} onClick={() => setIsModalOpen(true)}>
            Start New Cycle
          </button>
        )}
      </div>

      {isCycleActive && cycle ? (
        <>
          {/* ── Cycle Info Card ────────────────────────────────────────────── */}
          <div className={styles.cycleCard}>
            <span className={styles.cycleTitle}>{cycle.cycle_name}</span>
            <span className={styles.cycleMeta}>
              Target: {cycle.scope_department_name || "All Departments"} | {cycle.scope_location_name || "All Locations"}
            </span>
            <span className={styles.cycleMeta}>
              Timeline: {new Date(cycle.start_date).toLocaleDateString()} to {new Date(cycle.end_date).toLocaleDateString()}
            </span>
          </div>

          {/* ── Asset Verification Table ───────────────────────────────────── */}
          <div className={styles.tableContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Expected location</th>
                  <th style={{ textAlign: "center" }}>Verification</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <span className={styles.assetTag}>{item.asset_tag}</span> {item.asset_name}
                    </td>
                    <td>{item.remarks || "Assigned location"}</td>
                    <td style={{ textAlign: "center" }}>
                      <div className={styles.toggleGroup}>
                        <button 
                          className={`${styles.toggleBtn} ${item.verification_status === "Verified" ? styles.toggleVerifiedActive : ""}`}
                          onClick={() => handleVerification(item.id, "Verified")}
                        >
                          Verified
                        </button>
                        <button 
                          className={`${styles.toggleBtn} ${item.verification_status === "Missing" ? styles.toggleMissingActive : ""}`}
                          onClick={() => handleVerification(item.id, "Missing")}
                        >
                          Missing
                        </button>
                        <button 
                          className={`${styles.toggleBtn} ${item.verification_status === "Damaged" ? styles.toggleDamagedActive : ""}`}
                          onClick={() => handleVerification(item.id, "Damaged")}
                        >
                          Damaged
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ── Discrepancy Banner ───────────────────────────────────────── */}
          {flaggedCount > 0 && (
            <div className={styles.discrepancyBanner}>
              <span>{flaggedCount} assets flagged - discrepancy report generated automatically</span>
            </div>
          )}

          {/* ── Actions ────────────────────────────────────────────────────── */}
          <div style={{ marginTop: "var(--space-4)" }}>
            <button className={styles.primaryBtn} style={{ backgroundColor: "#1e3a5f" }} onClick={handleCloseCycle}>
              Close audit cycle
            </button>
          </div>
        </>
      ) : (
        <div className={styles.emptyState}>
          <h3 style={{ color: "var(--color-text)", marginBottom: "var(--space-2)" }}>No Active Audit Cycle</h3>
          <p>Click "Start New Cycle" to begin a new verification round.</p>
        </div>
      )}
      
      {/* ── New Cycle Modal ──────────────────────────────────────────────── */}
      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <span className={styles.modalTitle}>Start New Audit Cycle</span>
            <form onSubmit={handleCreateCycle} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Audit Scope (Title)</label>
                <input
                  className={styles.input}
                  placeholder="e.g. Q4 Audit: IT Dept"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  autoFocus
                />
              </div>

              <div className={styles.twoCol}>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Start Date</label>
                  <input
                    className={styles.input}
                    type="date"
                    value={newStartDate}
                    onChange={(e) => setNewStartDate(e.target.value)}
                  />
                </div>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>End Date</label>
                  <input
                    className={styles.input}
                    type="date"
                    value={newEndDate}
                    onChange={(e) => setNewEndDate(e.target.value)}
                  />
                </div>
              </div>

              <div className={styles.twoCol}>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Department Scope</label>
                  <select 
                    className={styles.select}
                    value={scopeDept}
                    onChange={(e) => setScopeDept(e.target.value)}
                  >
                    <option value="">All Departments</option>
                    {departments.map(d => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                </div>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Location Scope</label>
                  <select 
                    className={styles.select}
                    value={scopeLoc}
                    onChange={(e) => setScopeLoc(e.target.value)}
                  >
                    <option value="">All Locations</option>
                    {locations.map(l => (
                      <option key={l.id} value={l.id}>{l.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Select Auditors</label>
                <select 
                  className={styles.select} 
                  multiple
                  style={{ height: "100px" }}
                  value={selectedAuditors} 
                  onChange={(e) => {
                    const options = [...e.target.options];
                    const selected = options.filter(o => o.selected).map(o => o.value);
                    setSelectedAuditors(selected);
                  }}
                >
                  {employees.map(emp => (
                    <option key={emp.id} value={emp.id}>{emp.name}</option>
                  ))}
                </select>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-subtle)" }}>Hold Ctrl/Cmd to select multiple.</span>
              </div>

              <div className={styles.modalActions}>
                <button
                  type="button"
                  className={styles.cancelBtn}
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={styles.primaryBtn}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Starting..." : "Create Cycle"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
