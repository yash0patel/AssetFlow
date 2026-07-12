/**
 * pages/notifications/Notifications.jsx
 * ─────────────────────────────────────
 * Screen 10: Activity Logs & Notifications.
 */

import { useState, useEffect } from "react";
import notificationService from "@services/notification.service";
import styles from "./notifications.module.css";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

const TABS = ["All", "Alerts", "Approvals", "Bookings"];

const getCategoryParam = (tab) => {
  if (tab === "Alerts") return "Alert";
  if (tab === "Approvals") return "Approval";
  if (tab === "Bookings") return "Booking";
  return undefined;
};

const getTypeClass = (category) => {
  switch (category) {
    case "Alert": return styles.typeAlert;
    case "Approval": return styles.typeApproval;
    case "Booking": return styles.typeBooking;
    default: return "";
  }
};

export default function Notifications() {
  const [activeTab, setActiveTab] = useState("All");
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const category = getCategoryParam(activeTab);
      const data = await notificationService.listNotifications({
        category,
        page_size: 100,
      });
      setNotifications(data.items || []);
    } catch (err) {
      console.error("Failed to load notifications:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, [activeTab]);

  const toggleRead = async (id) => {
    try {
      await notificationService.markRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err) {
      console.error("Failed to mark notification read:", err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error("Failed to mark all read:", err);
    }
  };

  return (
    <div className={styles.container}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-4)" }}>
        <h1 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--color-text)", margin: 0 }}>
          Activity Logs & Notifications
        </h1>
        <button 
          onClick={handleMarkAllRead} 
          style={{ background: "none", border: "none", color: "var(--color-primary-600)", cursor: "pointer", fontSize: "0.875rem" }}
        >
          Mark all as read
        </button>
      </div>

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
        {loading ? (
          <div style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--color-text-subtle)" }}>
            Loading notifications...
          </div>
        ) : notifications.length > 0 ? (
          notifications.map((notif) => (
            <div key={notif.id} className={`${styles.item} ${getTypeClass(notif.category)}`}>
              <div className={styles.itemLeft}>
                <input
                  type="checkbox"
                  className={styles.readCheckbox}
                  checked={notif.is_read}
                  onChange={() => toggleRead(notif.id)}
                  disabled={notif.is_read}
                  title="Mark as read"
                />
                <span className={`${styles.message} ${!notif.is_read ? styles.messageUnread : ""}`}>
                  {notif.message}
                </span>
              </div>
              <span className={styles.time}>{dayjs(notif.created_at).fromNow()}</span>
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
