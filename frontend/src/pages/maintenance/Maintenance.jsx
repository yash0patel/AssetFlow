/**
 * pages/maintenance/Maintenance.jsx
 * ─────────────────────────────────
 * Screen 7: Maintenance Kanban Board.
 */

import { useState, useEffect } from "react";
import toast from "react-hot-toast";
import assetService from "@services/asset.service";
import maintenanceService from "@services/maintenance.service";
import styles from "./maintenance.module.css";

const COLUMNS = ["Pending", "Approved", "Technician Assigned", "In Progress", "Resolved"];

export default function Maintenance() {
  const [tickets, setTickets] = useState([]);
  const [assets, setAssets] = useState([]);
  const [technicians, setTechnicians] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // New Request Modal state
  const [isRaiseModalOpen, setIsRaiseModalOpen] = useState(false);
  const [newAsset, setNewAsset] = useState("");
  const [newIssue, setNewIssue] = useState("");
  const [newPriority, setNewPriority] = useState("Medium");
  
  // Edit Ticket Modal state
  const [activeTicket, setActiveTicket] = useState(null);
  const [editStatus, setEditStatus] = useState("");
  const [editTech, setEditTech] = useState("");
  const [editNote, setEditNote] = useState("");
  const [editCost, setEditCost] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadRequests = async () => {
    try {
      const data = await maintenanceService.listMaintenanceRequests({ page_size: 100 });
      setTickets(data.items || []);
    } catch (err) {
      console.error("Error loading requests:", err);
    }
  };

  const loadAssetsAndTechs = async () => {
    try {
      const [assetsData, techsData] = await Promise.all([
        assetService.listAssets({ page_size: 100 }),
        maintenanceService.listTechnicians(),
      ]);
      setAssets(assetsData.items || []);
      setTechnicians(techsData);
    } catch (err) {
      console.error("Error loading assets/techs:", err);
    }
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([loadRequests(), loadAssetsAndTechs()]).finally(() => setLoading(false));
  }, []);

  const handleRaiseRequest = async (e) => {
    e.preventDefault();
    if (!newAsset || !newIssue.trim()) {
      toast.error("Please select an asset and describe the issue.");
      return;
    }
    
    setIsSubmitting(true);
    try {
      await maintenanceService.raiseRequest({
        asset_id: newAsset,
        issue_description: newIssue,
        priority: newPriority,
      });
      toast.success("Maintenance request raised successfully.");
      setIsRaiseModalOpen(false);
      setNewAsset("");
      setNewIssue("");
      setNewPriority("Medium");
      await loadRequests();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to raise request.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const openTicketModal = (ticket) => {
    setActiveTicket(ticket);
    setEditStatus(ticket.status);
    setEditTech(ticket.technician_id || "");
    setEditNote(ticket.resolution_notes || "");
    setEditCost(ticket.actual_cost || "");
  };

  const handleUpdateTicket = async (e) => {
    e.preventDefault();
    if (!activeTicket) return;

    setIsSubmitting(true);
    try {
      // Transition logic depending on target status
      if (activeTicket.status === "Pending") {
        if (editStatus === "Rejected") {
          const reason = window.prompt("Enter rejection reason:") || "Rejected";
          await maintenanceService.rejectRequest(activeTicket.id, { rejection_reason: reason });
        } else if (editStatus === "Approved" || editStatus === "Technician Assigned") {
          await maintenanceService.approveRequest(activeTicket.id, {
            technician_id: editTech || null,
          });
        }
      } else if (activeTicket.status === "Approved") {
        if (editTech) {
          await maintenanceService.approveRequest(activeTicket.id, {
            technician_id: editTech,
          });
        }
      } else if (activeTicket.status === "Technician Assigned") {
        if (editStatus === "In Progress") {
          await maintenanceService.startRequest(activeTicket.id);
        }
      } else if (activeTicket.status === "In Progress" || activeTicket.status === "Technician Assigned" || activeTicket.status === "Approved") {
        if (editStatus === "Resolved") {
          await maintenanceService.resolveRequest(activeTicket.id, {
            resolution_notes: editNote || "Resolved",
            actual_cost: editCost ? parseFloat(editCost) : null,
          });
        }
      }

      toast.success("Ticket updated successfully.");
      setActiveTicket(null);
      await loadRequests();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update ticket.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading && tickets.length === 0) {
    return <div className={styles.container}>Loading maintenance board...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.pageTitle}>Maintenance Board</h1>
        <button className={styles.primaryBtn} onClick={() => setIsRaiseModalOpen(true)}>
          Raise Request
        </button>
      </div>

      <div className={styles.board}>
        {COLUMNS.map((colName) => (
          <div key={colName} className={styles.column}>
            <div className={styles.columnHeader}>{colName}</div>
            <div className={styles.columnBody}>
              {tickets.filter((t) => t.status.toLowerCase() === colName.toLowerCase()).map((ticket) => (
                <div 
                  key={ticket.id} 
                  className={`${styles.card} ${ticket.status === "Resolved" ? styles.cardResolved : ""}`}
                  onClick={() => openTicketModal(ticket)}
                >
                  <span className={styles.assetTag}>{ticket.asset_tag}</span>
                  <span className={styles.issueDesc}>{ticket.issue_description}</span>
                  
                  {ticket.technician_name && ticket.status !== "Resolved" && (
                    <span className={styles.techName}>Tech: {ticket.technician_name}</span>
                  )}
                  {ticket.status === "Resolved" && ticket.resolution_notes && (
                    <span className={styles.statusDetail}>{ticket.resolution_notes}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* ── Raise Request Modal ────────────────────────────────────────────── */}
      {isRaiseModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <span className={styles.modalTitle}>Raise Maintenance Request</span>
            <form onSubmit={handleRaiseRequest} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Asset</label>
                <select 
                  className={styles.select} 
                  value={newAsset} 
                  onChange={(e) => setNewAsset(e.target.value)}
                >
                  <option value="">Select Asset...</option>
                  {assets.map(a => (
                    <option key={a.id} value={a.id}>{a.asset_tag} - {a.name} ({a.current_status})</option>
                  ))}
                </select>
              </div>

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Issue Description</label>
                <textarea 
                  className={styles.textarea} 
                  placeholder="Describe the problem..."
                  value={newIssue}
                  onChange={(e) => setNewIssue(e.target.value)}
                />
              </div>
              
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Priority</label>
                <select className={styles.select} value={newPriority} onChange={(e) => setNewPriority(e.target.value)}>
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                  <option>Critical</option>
                </select>
              </div>

              <div className={styles.modalActions}>
                <button type="button" className={styles.cancelBtn} onClick={() => setIsRaiseModalOpen(false)}>Cancel</button>
                <button type="submit" className={styles.primaryBtn} disabled={isSubmitting}>
                  {isSubmitting ? "Submitting..." : "Submit Request"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Edit Ticket Modal ──────────────────────────────────────────────── */}
      {activeTicket && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <span className={styles.modalTitle}>Update Ticket: {activeTicket.asset_tag}</span>
            <form onSubmit={handleUpdateTicket} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
              
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Status</label>
                <select 
                  className={styles.select} 
                  value={editStatus} 
                  onChange={(e) => setEditStatus(e.target.value)}
                >
                  {/* Let user transition depending on current state */}
                  <option value={activeTicket.status}>{activeTicket.status}</option>
                  {activeTicket.status === "Pending" && (
                    <>
                      <option value="Approved">Approve</option>
                      <option value="Rejected">Reject</option>
                    </>
                  )}
                  {activeTicket.status === "Approved" && (
                    <option value="Technician Assigned">Assign Technician</option>
                  )}
                  {activeTicket.status === "Technician Assigned" && (
                    <option value="In Progress">Start Work</option>
                  )}
                  {(activeTicket.status === "In Progress" || activeTicket.status === "Technician Assigned" || activeTicket.status === "Approved") && (
                    <option value="Resolved">Resolve</option>
                  )}
                </select>
              </div>

              {/* Technician assignment input */}
              {(editStatus === "Approved" || editStatus === "Technician Assigned" || activeTicket.status === "Approved" || activeTicket.status === "Technician Assigned") && (
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Assigned Technician</label>
                  <select 
                    className={styles.select} 
                    value={editTech} 
                    onChange={(e) => setEditTech(e.target.value)}
                  >
                    <option value="">Select Technician...</option>
                    {technicians.map(t => (
                      <option key={t.id} value={t.id}>{t.name} ({t.specialization})</option>
                    ))}
                  </select>
                </div>
              )}
              
              {editStatus === "Resolved" && (
                <>
                  <div className={styles.fieldGroup}>
                    <label className={styles.fieldLabel}>Resolution Notes</label>
                    <textarea 
                      className={styles.textarea} 
                      placeholder="E.g. replaced screen..."
                      value={editNote}
                      onChange={(e) => setEditNote(e.target.value)}
                    />
                  </div>
                  <div className={styles.fieldGroup}>
                    <label className={styles.fieldLabel}>Actual Cost (₹)</label>
                    <input 
                      type="number" 
                      className={styles.input} 
                      placeholder="E.g. 5000"
                      value={editCost}
                      onChange={(e) => setEditCost(e.target.value)}
                    />
                  </div>
                </>
              )}

              <div className={styles.footerNote}>
                Approving moves asset to <b>Under Maintenance</b>.<br/>
                Resolving returns it to <b>Available</b>.
              </div>

              <div className={styles.modalActions}>
                <button type="button" className={styles.cancelBtn} onClick={() => setActiveTicket(null)}>Cancel</button>
                <button type="submit" className={styles.primaryBtn} disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
