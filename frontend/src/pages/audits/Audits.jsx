/**
 * pages/audits/Audits.jsx
 * ───────────────────────
 * Screen 8: Asset Audit Screen.
 */

import { useState } from "react";
import toast from "react-hot-toast";
import { MOCK_ACTIVE_AUDIT } from "./mockAudits";
import styles from "./audit.module.css";

export default function Audits() {
  const [cycle, setCycle] = useState(MOCK_ACTIVE_AUDIT);
  const [isCycleActive, setIsCycleActive] = useState(true);
  
  // State for new cycle modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDateRange, setNewDateRange] = useState("");
  const [newAuditors, setNewAuditors] = useState("");

  const handleVerification = (assetId, status) => {
    if (!isCycleActive) return;
    
    setCycle(prev => ({
      ...prev,
      assets: prev.assets.map(a => 
        a.id === assetId ? { ...a, verification: status } : a
      )
    }));
  };

  const handleCloseCycle = () => {
    if (cycle.assets.some(a => !a.verification)) {
      if (!window.confirm("Some assets are not yet verified. Close anyway?")) {
        return;
      }
    }
    
    setIsCycleActive(false);
    toast.success("Audit cycle closed successfully. Discrepancy report generated.");
  };

  const handleCreateCycle = (e) => {
    e.preventDefault();
    if (!newTitle.trim()) {
      toast.error("Please provide an audit title/scope.");
      return;
    }
    
    setCycle({
      id: `aud${Date.now()}`,
      title: newTitle,
      date_range: newDateRange || "Not specified",
      auditors: newAuditors || "Unassigned",
      assets: [
        // Inject some random unverified assets for the new cycle mock
        { id: "a10", tag: "AF-1011", name: "Desk phone", location: "HQ Floor 2", verification: null },
        { id: "a11", tag: "AF-1012", name: "MacBook Pro", location: "HQ Floor 2", verification: null },
      ]
    });
    
    setIsCycleActive(true);
    setIsModalOpen(false);
    toast.success("New audit cycle started.");
    
    // Reset form
    setNewTitle("");
    setNewDateRange("");
    setNewAuditors("");
  };

  const flaggedCount = cycle.assets.filter(a => a.verification === "Missing" || a.verification === "Damaged").length;

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

      {isCycleActive ? (
        <>
          {/* ── Cycle Info Card ────────────────────────────────────────────── */}
          <div className={styles.cycleCard}>
            <span className={styles.cycleTitle}>{cycle.title} - {cycle.date_range}</span>
            <span className={styles.cycleMeta}>Auditors: {cycle.auditors}</span>
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
                {cycle.assets.map((asset) => (
                  <tr key={asset.id}>
                    <td>
                      <span className={styles.assetTag}>{asset.tag}</span> {asset.name}
                    </td>
                    <td>{asset.location}</td>
                    <td style={{ textAlign: "center" }}>
                      <div className={styles.toggleGroup}>
                        <button 
                          className={`${styles.toggleBtn} ${asset.verification === "Verified" ? styles.toggleVerifiedActive : ""}`}
                          onClick={() => handleVerification(asset.id, "Verified")}
                        >
                          Verified
                        </button>
                        <button 
                          className={`${styles.toggleBtn} ${asset.verification === "Missing" ? styles.toggleMissingActive : ""}`}
                          onClick={() => handleVerification(asset.id, "Missing")}
                        >
                          Missing
                        </button>
                        <button 
                          className={`${styles.toggleBtn} ${asset.verification === "Damaged" ? styles.toggleDamagedActive : ""}`}
                          onClick={() => handleVerification(asset.id, "Damaged")}
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
              <button className={styles.reportLink} onClick={() => toast("Opening report... (Mock)")}>
                View Report
              </button>
            </div>
          )}

          {/* ── Actions ────────────────────────────────────────────────────── */}
          <div style={{ marginTop: "var(--space-2)" }}>
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

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Date Range</label>
                <input
                  className={styles.input}
                  placeholder="e.g. 1-15 Nov"
                  value={newDateRange}
                  onChange={(e) => setNewDateRange(e.target.value)}
                />
              </div>
              
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Assigned Auditors</label>
                <input
                  className={styles.input}
                  placeholder="e.g. J. Doe, S. Smith"
                  value={newAuditors}
                  onChange={(e) => setNewAuditors(e.target.value)}
                />
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
                >
                  Create Cycle
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
