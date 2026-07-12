/**
 * pages/maintenance/Maintenance.jsx
 * ─────────────────────────────────
 * Screen 7: Maintenance Kanban Board.
 */

import { useState } from "react";
import toast from "react-hot-toast";
import { MOCK_MAINTENANCE_TICKETS, MOCK_ASSETS_LIST } from "./mockMaintenance";
import styles from "./maintenance.module.css";

const COLUMNS = ["Pending", "Approved", "Technician assigned", "in progress", "Resolved"];

export default function Maintenance() {
  const [tickets, setTickets] = useState(MOCK_MAINTENANCE_TICKETS);
  
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

  const handleRaiseRequest = (e) => {
    e.preventDefault();
    if (!newAsset || !newIssue) {
      toast.error("Please select an asset and describe the issue.");
      return;
    }
    
    const assetObj = MOCK_ASSETS_LIST.find((a) => a.id === newAsset);
    
    const newTicket = {
      id: `m${Date.now()}`,
      asset_tag: assetObj.tag,
      asset_name: assetObj.name,
      issue: newIssue,
      status: "Pending",
      priority: newPriority,
      technician: null,
      resolution_note: null,
    };
    
    setTickets([...tickets, newTicket]);
    toast.success("Maintenance request raised successfully.");
    setIsRaiseModalOpen(false);
    setNewAsset("");
    setNewIssue("");
    setNewPriority("Medium");
  };

  const openTicketModal = (ticket) => {
    setActiveTicket(ticket);
    setEditStatus(ticket.status);
    setEditTech(ticket.technician || "");
    setEditNote(ticket.resolution_note || "");
  };

  const handleUpdateTicket = (e) => {
    e.preventDefault();
    
    setTickets((prev) => prev.map(t => {
      if (t.id === activeTicket.id) {
        return {
          ...t,
          status: editStatus,
          technician: editTech,
          resolution_note: editStatus === "Resolved" ? (editNote || `Resolved on ${new Date().toLocaleDateString()}`) : editNote
        };
      }
      return t;
    }));
    
    toast.success("Ticket updated.");
    setActiveTicket(null);
  };

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
              {tickets.filter((t) => t.status === colName).map((ticket) => (
                <div 
                  key={ticket.id} 
                  className={`${styles.card} ${ticket.status === "Resolved" ? styles.cardResolved : ""}`}
                  onClick={() => openTicketModal(ticket)}
                >
                  <span className={styles.assetTag}>{ticket.asset_tag}</span>
                  <span className={styles.issueDesc}>{ticket.issue}</span>
                  
                  {ticket.technician && ticket.status !== "Resolved" && (
                    <span className={styles.techName}>Tech: {ticket.technician}</span>
                  )}
                  {ticket.status === "Resolved" && ticket.resolution_note && (
                    <span className={styles.statusDetail}>{ticket.resolution_note}</span>
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
                  {MOCK_ASSETS_LIST.map(a => (
                    <option key={a.id} value={a.id}>{a.tag} - {a.name}</option>
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

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Attach Photo</label>
                <input type="file" className={styles.fileInput} accept="image/*" />
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-subtle)' }}>*Mock upload</span>
              </div>

              <div className={styles.modalActions}>
                <button type="button" className={styles.cancelBtn} onClick={() => setIsRaiseModalOpen(false)}>Cancel</button>
                <button type="submit" className={styles.primaryBtn}>Submit Request</button>
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
                  {COLUMNS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Assigned Technician</label>
                <input 
                  className={styles.input} 
                  placeholder="Technician name..."
                  value={editTech}
                  onChange={(e) => setEditTech(e.target.value)}
                />
              </div>
              
              {editStatus === "Resolved" && (
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Resolution Notes</label>
                  <textarea 
                    className={styles.textarea} 
                    placeholder="E.g. replaced bulb..."
                    value={editNote}
                    onChange={(e) => setEditNote(e.target.value)}
                  />
                </div>
              )}

              <div className={styles.footerNote}>
                Approving moves asset to <b>Under Maintenance</b>.<br/>
                Resolving returns it to <b>Available</b>.
              </div>

              <div className={styles.modalActions}>
                <button type="button" className={styles.cancelBtn} onClick={() => setActiveTicket(null)}>Cancel</button>
                <button type="submit" className={styles.primaryBtn}>Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
