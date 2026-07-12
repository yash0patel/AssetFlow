/**
 * pages/allocation/Allocations.jsx
 * ──────────────────────────────────
 * Screen 5: Asset Allocation & Transfer.
 *
 * Tabs:
 *   0 – Allocate/Transfer (conflict-aware form)
 *   1 – Active Allocations (with overdue flag + return action)
 *   2 – Transfer Requests (pending approvals)
 */

import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import dayjs from "dayjs";
import assetService from "@services/asset.service";
import employeeService from "@services/employee.service";
import allocationService from "@services/allocation.service";
import styles from "./allocation.module.css";

const MAIN_TABS = ["Allocate / Transfer", "Active Allocations", "Transfer Requests"];

const TRANSFER_STATUS_CLASS = {
  Requested: styles.badgeRequested,
  Approved:  styles.badgeApproved,
  Rejected:  styles.badgeOverdue,
  Completed: styles.badgeReturned,
  Cancelled: styles.badgeReturned,
};

export default function Allocations() {
  const [mainTab,  setMainTab]  = useState(0);

  // ── Options state ──────────────────────────────────────────────────────────
  const [allAssets, setAllAssets] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  // ── Tab 0: Allocate / Transfer state ───────────────────────────────────────
  const [selectedAssetId,   setSelectedAssetId]   = useState("");
  const [selectedEmployee,  setSelectedEmployee]   = useState("");
  const [expectedReturn,    setExpectedReturn]     = useState("");
  const [transferTo,        setTransferTo]         = useState("");
  const [transferReason,    setTransferReason]     = useState("");
  const [isSubmitting,      setIsSubmitting]       = useState(false);
  const [selectedAssetHistory, setSelectedAssetHistory] = useState([]);

  // ── Tab 1: Active Allocations state ───────────────────────────────────────
  const [allocations, setAllocations] = useState([]);
  const [returnModal, setReturnModal] = useState(null); // id
  const [returnNotes, setReturnNotes] = useState("");
  const [returnCondition, setReturnCondition] = useState("Good");

  // ── Tab 2: Transfer Requests state ────────────────────────────────────────
  const [transfers, setTransfers] = useState([]);

  // ── Load core options ──────────────────────────────────────────────────────
  const loadOptions = async () => {
    try {
      const [assetsData, empsData] = await Promise.all([
        assetService.listAssets({ page_size: 100 }),
        employeeService.listEmployees({ page_size: 100 }),
      ]);
      setAllAssets(assetsData.items || []);
      setEmployees(empsData.items || []);
    } catch (err) {
      console.error("Error loading allocation options:", err);
    }
  };

  const loadAllocations = async () => {
    try {
      const data = await allocationService.listAllocations();
      setAllocations(data.items || []);
    } catch (err) {
      console.error("Error loading allocations:", err);
    }
  };

  const loadTransfers = async () => {
    try {
      const data = await allocationService.listTransfers();
      setTransfers(data.items || []);
    } catch (err) {
      console.error("Error loading transfers:", err);
    }
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([loadOptions(), loadAllocations(), loadTransfers()]).finally(() => setLoading(false));
  }, []);

  // ── Derived: selected asset object ────────────────────────────────────────
  const selectedAsset = allAssets.find((a) => a.id === selectedAssetId);
  const isConflict    = selectedAsset && (selectedAsset.current_status === "Allocated" || selectedAsset.current_holder_employee_id);

  // Load selected asset status/allocation history
  useEffect(() => {
    if (selectedAssetId) {
      assetService.getAsset(selectedAssetId).then(data => {
        setSelectedAssetHistory(data.status_history || []);
      }).catch(err => console.error("Error loading asset details for history:", err));
    } else {
      setSelectedAssetHistory([]);
    }
  }, [selectedAssetId]);

  // ── Handlers: Allocate ────────────────────────────────────────────────────
  const handleAllocate = async () => {
    if (!selectedAssetId || !selectedEmployee) {
      toast.error("Select an asset and an employee.");
      return;
    }
    setIsSubmitting(true);
    try {
      await allocationService.allocateAsset({
        asset_id: selectedAssetId,
        allocated_to_employee_id: selectedEmployee,
        expected_return_date: expectedReturn || null,
      });
      toast.success("Asset allocated successfully.");
      setSelectedAssetId("");
      setSelectedEmployee("");
      setExpectedReturn("");
      // Reload states
      await Promise.all([loadOptions(), loadAllocations()]);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to allocate asset.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Handlers: Transfer Request ─────────────────────────────────────────────
  const handleTransferRequest = async () => {
    if (!transferTo || !transferReason.trim()) {
      toast.error("Select destination employee and provide a reason.");
      return;
    }

    // Find the active allocation ID for this asset
    const activeAlloc = allocations.find(a => a.asset_id === selectedAssetId && a.status === "Active");
    if (!activeAlloc) {
      toast.error("Could not find an active allocation to transfer from.");
      return;
    }

    setIsSubmitting(true);
    try {
      await allocationService.createTransferRequest(activeAlloc.id, {
        to_employee_id: transferTo,
        reason: transferReason,
      });
      toast.success("Transfer request submitted for approval.");
      setTransferTo("");
      setTransferReason("");
      setSelectedAssetId("");
      await Promise.all([loadOptions(), loadTransfers()]);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to submit transfer request.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Handlers: Return ──────────────────────────────────────────────────────
  const openReturnModal = (id) => setReturnModal(id);
  const handleReturn = async () => {
    setIsSubmitting(true);
    try {
      await allocationService.returnAsset(returnModal, {
        return_condition: returnCondition,
        return_notes: returnNotes || null,
      });
      toast.success("Asset marked as returned.");
      setReturnModal(null);
      setReturnNotes("");
      setReturnCondition("Good");
      await Promise.all([loadOptions(), loadAllocations()]);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to return asset.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Handlers: Approve / Reject Transfer ───────────────────────────────────
  const handleTransferApproval = async (id, approve) => {
    try {
      if (approve) {
        await allocationService.approveTransfer(id);
        toast.success("Transfer request approved.");
      } else {
        const rejectionReason = window.prompt("Enter rejection reason:");
        if (rejectionReason === null) return; // cancel prompt
        await allocationService.rejectTransfer(id, { rejection_reason: rejectionReason || "Rejected" });
        toast.success("Transfer request rejected.");
      }
      await Promise.all([loadOptions(), loadAllocations(), loadTransfers()]);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to process transfer request.");
    }
  };

  if (loading) {
    return <div className={styles.container}>Loading allocations data...</div>;
  }

  return (
    <div className={styles.container}>
      {/* ── Main Tab Bar ─────────────────────────────────────────────────── */}
      <div className={styles.tabs}>
        {MAIN_TABS.map((t, i) => (
          <button
            key={t}
            className={`${styles.tab} ${mainTab === i ? styles.tabActive : ""}`}
            onClick={() => setMainTab(i)}
          >
            {t}
          </button>
        ))}
      </div>

      {/* ══ TAB 0: Allocate / Transfer ═══════════════════════════════════════ */}
      {mainTab === 0 && (
        <>
          {/* Asset picker */}
          <div className={styles.assetField}>
            <span className={styles.fieldLabel}>Asset</span>
            <select
              className={styles.assetSelect}
              value={selectedAssetId}
              onChange={(e) => {
                setSelectedAssetId(e.target.value);
                setSelectedEmployee("");
                setTransferTo("");
                setTransferReason("");
              }}
            >
              <option value="">Select an asset…</option>
              {allAssets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.asset_tag} – {a.name} ({a.current_status})
                </option>
              ))}
            </select>
          </div>

          {selectedAsset && (
            <>
              {/* ── Conflict detected ─────────────────────────────────────── */}
              {isConflict ? (
                <>
                  <div className={styles.conflictBanner}>
                    <span className={styles.conflictTitle}>
                      Already Allocated to {selectedAsset.current_holder_name || "another owner"}
                    </span>
                    <span className={styles.conflictSub}>
                      Direct re-allocation is blocked — submit a transfer request below
                    </span>
                  </div>

                  {/* Transfer Request form */}
                  <span className={styles.sectionTitle}>Transfer Request</span>
                  <div className={styles.card}>
                    <div className={styles.twoCol}>
                      <div className={styles.fieldGroup}>
                        <label className={styles.label}>From</label>
                        <input
                          className={styles.input}
                          value={selectedAsset.current_holder_name || "Current Holder"}
                          disabled
                        />
                      </div>
                      <div className={styles.fieldGroup}>
                        <label className={styles.label}>To</label>
                        <select
                          className={styles.select}
                          value={transferTo}
                          onChange={(e) => setTransferTo(e.target.value)}
                        >
                          <option value="">Select Employee…</option>
                          {employees.filter(
                            (emp) => emp.id !== selectedAsset.current_holder_employee_id
                          ).map((emp) => (
                            <option key={emp.id} value={emp.id}>
                              {emp.name} – {emp.department_name}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div className={styles.fieldGroup}>
                      <label className={styles.label}>Reason</label>
                      <textarea
                        className={styles.textarea}
                        placeholder="Explain why this asset needs to be transferred…"
                        value={transferReason}
                        onChange={(e) => setTransferReason(e.target.value)}
                      />
                    </div>

                    <button
                      className={styles.primaryBtn}
                      disabled={isSubmitting}
                      onClick={handleTransferRequest}
                    >
                      {isSubmitting ? "Submitting…" : "Submit Request"}
                    </button>
                  </div>
                </>
              ) : (
                /* ── Available: direct allocation form ───────────────────── */
                <>
                  <span className={styles.sectionTitle}>Allocate Asset</span>
                  <div className={styles.card}>
                    <div className={styles.twoCol}>
                      <div className={styles.fieldGroup}>
                        <label className={styles.label}>Assign to Employee</label>
                        <select
                          className={styles.select}
                          value={selectedEmployee}
                          onChange={(e) => setSelectedEmployee(e.target.value)}
                        >
                          <option value="">Select Employee…</option>
                          {employees.map((emp) => (
                            <option key={emp.id} value={emp.id}>
                              {emp.name} – {emp.department_name}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className={styles.fieldGroup}>
                        <label className={styles.label}>Expected Return Date (optional)</label>
                        <input
                          className={styles.input}
                          type="date"
                          value={expectedReturn}
                          onChange={(e) => setExpectedReturn(e.target.value)}
                        />
                      </div>
                    </div>

                    <button
                      className={styles.primaryBtn}
                      disabled={isSubmitting}
                      onClick={handleAllocate}
                    >
                      {isSubmitting ? "Allocating…" : "Allocate Asset"}
                    </button>
                  </div>
                </>
              )}

              {/* ── Status History (always shown) ──────────────────────── */}
              <span className={styles.sectionTitle}>Status / Transaction History</span>
              <div className={styles.historyList}>
                {selectedAssetHistory.length > 0 ? (
                  selectedAssetHistory.map((h, i) => (
                    <div key={i} className={styles.historyItem}>
                      <span className={styles.historyDate}>{new Date(h.changed_at).toLocaleString()}</span>
                      <span>
                        Changed status to <strong>{h.new_status}</strong> {h.remarks ? `(${h.remarks})` : ""}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className={styles.historyItem}>No transition history available.</div>
                )}
              </div>
            </>
          )}
        </>
      )}

      {/* ══ TAB 1: Active Allocations ═════════════════════════════════════════ */}
      {mainTab === 1 && (
        <>
          <div className={styles.tableContainer}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Target</th>
                  <th>Type</th>
                  <th>Allocated On</th>
                  <th>Expected Return</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {allocations.map((alloc) => (
                  <tr
                    key={alloc.id}
                    className={alloc.is_overdue ? styles.overdueRow : ""}
                  >
                    <td>
                      <span className={styles.monoText}>{alloc.asset_tag}</span>
                      <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginTop: "2px" }}>
                        {alloc.asset_name}
                      </div>
                    </td>
                    <td className={styles.primaryText}>
                      {alloc.allocated_to_employee_name || alloc.allocated_to_department_name}
                    </td>
                    <td>{alloc.allocated_to_employee_id ? "Employee" : "Department"}</td>
                    <td>{new Date(alloc.allocation_date).toLocaleDateString()}</td>
                    <td>
                      {alloc.expected_return_date
                        ? alloc.expected_return_date
                        : <span style={{ color: "var(--color-text-subtle)" }}>—</span>}
                    </td>
                    <td>
                      <span
                        className={`${styles.badge} ${
                          alloc.is_overdue ? styles.badgeOverdue :
                          alloc.status === "Returned" ? styles.badgeReturned :
                          styles.badgeActive
                        }`}
                      >
                        {alloc.status}
                      </span>
                    </td>
                    <td>
                      {alloc.status === "Active" && (
                        <button
                          className={`${styles.actionLink}`}
                          onClick={() => openReturnModal(alloc.id)}
                        >
                          Mark Returned
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Return modal — inline lightweight */}
          {returnModal && (
            <div className={styles.card} style={{ border: "1px solid var(--color-primary-300)", marginTop: "1rem" }}>
              <span className={styles.sectionTitle}>Return Check-in</span>
              <div className={styles.twoCol}>
                <div className={styles.fieldGroup}>
                  <label className={styles.label}>Condition on Return</label>
                  <select
                    className={styles.select}
                    value={returnCondition}
                    onChange={(e) => setReturnCondition(e.target.value)}
                  >
                    {["New", "Good", "Fair", "Poor", "Damaged"].map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className={styles.fieldGroup}>
                <label className={styles.label}>Return Notes</label>
                <textarea
                  className={styles.textarea}
                  placeholder="Any observations on return…"
                  value={returnNotes}
                  onChange={(e) => setReturnNotes(e.target.value)}
                />
              </div>
              <div style={{ display: "flex", gap: "var(--space-4)" }}>
                <button className={styles.primaryBtn} disabled={isSubmitting} onClick={handleReturn}>
                  {isSubmitting ? "Saving…" : "Confirm Return"}
                </button>
                <button
                  className={styles.primaryBtn}
                  style={{ background: "transparent", color: "var(--color-text-muted)", border: "1px solid var(--color-border)" }}
                  onClick={() => setReturnModal(null)}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* ══ TAB 2: Transfer Requests ══════════════════════════════════════════ */}
      {mainTab === 2 && (
        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Asset</th>
                <th>From</th>
                <th>To</th>
                <th>Reason</th>
                <th>Requested On</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {transfers.map((tr) => (
                <tr key={tr.id}>
                  <td>
                    <span className={styles.monoText}>{tr.asset_tag}</span>
                    <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginTop: "2px" }}>
                      {tr.asset_name}
                    </div>
                  </td>
                  <td>{tr.from_employee_name}</td>
                  <td className={styles.primaryText}>{tr.to_employee_name}</td>
                  <td style={{ maxWidth: "200px", fontSize: "0.875rem" }}>{tr.reason}</td>
                  <td>{new Date(tr.created_at).toLocaleDateString()}</td>
                  <td>
                    <span className={`${styles.badge} ${TRANSFER_STATUS_CLASS[tr.status] || ""}`}>
                      {tr.status}
                    </span>
                  </td>
                  <td>
                    {tr.status === "Requested" && (
                      <div style={{ display: "flex", gap: "var(--space-3)" }}>
                        <button
                          className={styles.actionLink}
                          onClick={() => handleTransferApproval(tr.id, true)}
                        >
                          Approve
                        </button>
                        <button
                          className={`${styles.actionLink} ${styles.dangerLink}`}
                          onClick={() => handleTransferApproval(tr.id, false)}
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
