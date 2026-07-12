/**
 * pages/notifications/Notifications.jsx
 * ─────────────────────────────────────
 * Screen 10: Activity Logs & Notifications.
 */

import { useState } from "react";
import styles from "./notifications.module.css";

const TABS = ["All", "Alerts", "Approvals", "Bookings"];

// Mock data strictly following user's prompt mockup
const INITIAL_NOTIFICATIONS = [
  {
    id: "n1",
    message: "Laptop AF-0014 assigned to Priya shah",
    time: "2m ago",
    type: "Approvals", // generic admin action
    read: false,
  },
  {
    id: "n2",
    message: "Maintenance request AF-0055 approved",
    time: "18m ago",
    type: "Approvals",
    read: false,
  },
  {
    id: "n3",
    message: "Booking confirmed : Room B2 : 2:00 to 3:00 PM",
    time: "1h ago",
    type: "Bookings",
    read: false,
  },
  {
    id: "n4",
    message: "Transfer approved : AF-0033 to facilities dept",
    time: "3h ago",
    type: "Approvals",
    read: false,
  },
  {
    id: "n5",
    message: "Overdue return : AF-0021 was due 3 days ago",
    time: "1d ago",
    type: "Alerts",
    read: false,
  },
  {
    id: "n6",
    message: "audit discrepancy flagged : AF-0088 damaged",
    time: "2d ago",
    type: "Alerts",
    read: false,
  },
];

const getTypeClass = (type) => {
  switch (type) {
    case "Alerts": return styles.typeAlert;
    case "Approvals": return styles.typeApproval;
    case "Bookings": return styles.typeBooking;
    default: return "";
  }
};

export default function Notifications() {
  const [activeTab, setActiveTab] = useState("All");
  const [notifications, setNotifications] = useState(INITIAL_NOTIFICATIONS);

  const filteredNotifications = notifications.filter(
    (n) => activeTab === "All" || n.type === activeTab
  );

  const toggleRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: !n.read } : n))
    );
  };

  return (
    <div className={styles.container}>
      <h1 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--color-text)", marginBottom: "var(--space-2)" }}>
        Activity Logs & Notifications
      </h1>

      {/* ── Tabs ─────────────────────────────────────────────────────────── */}
      <div className={styles.tabs}>
        {TABS.map((tab) => (
          <button
            key={tab}
            className={`${styles.tab} ${activeTab === tab ? styles.tabActive : ""}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* ── List ─────────────────────────────────────────────────────────── */}
      <div className={styles.list}>
        {filteredNotifications.length > 0 ? (
          filteredNotifications.map((notif) => (
            <div key={notif.id} className={`${styles.item} ${getTypeClass(notif.type)}`}>
              <div className={styles.itemLeft}>
                <input
                  type="checkbox"
                  className={styles.readCheckbox}
                  checked={notif.read}
                  onChange={() => toggleRead(notif.id)}
                  title="Mark as read/unread"
                />
                <span className={`${styles.message} ${!notif.read ? styles.messageUnread : ""}`}>
                  {notif.message}
                </span>
              </div>
              <span className={styles.time}>{notif.time}</span>
            </div>
          ))
        ) : (
          <div style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--color-text-subtle)" }}>
            No notifications in this category.
          </div>
        )}
      </div>
    </div>
  );
}
