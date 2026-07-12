/**
 * pages/bookings/Bookings.jsx
 * ────────────────────────────
 * Screen 6: Resource Booking Screen.
 */

import { useState, useMemo } from "react";
import toast from "react-hot-toast";
import dayjs from "dayjs";
import { MOCK_BOOKABLE_RESOURCES, MOCK_BOOKINGS } from "./mockBookings";
import styles from "./bookings.module.css";

const STATUS_CLASS = {
  Upcoming:  styles.badgeUpcoming,
  Ongoing:   styles.badgeOngoing,
  Completed: styles.badgeCompleted,
  Cancelled: styles.badgeCancelled,
};

// Timeline configuration (9 AM to 6 PM)
const START_HOUR = 9;
const END_HOUR = 18;
const PIXELS_PER_MINUTE = 1; // 60px per hour

// Helper to convert "HH:mm" to minutes since START_HOUR
function timeToOffset(timeStr) {
  const [h, m] = timeStr.split(":").map(Number);
  return (h - START_HOUR) * 60 + m;
}

// Check if two time ranges overlap (Exclusive of boundaries, so 10:00-11:00 and 11:00-12:00 do NOT overlap)
function checkOverlap(s1, e1, s2, e2) {
  return s1 < e2 && s2 < e1;
}

export default function Bookings() {
  const [selectedResource, setSelectedResource] = useState(MOCK_BOOKABLE_RESOURCES[0].id);
  // Default to the mock date
  const [selectedDate, setSelectedDate] = useState("2026-07-07"); 
  
  const [bookings, setBookings] = useState(MOCK_BOOKINGS);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // New Booking State
  const [newTitle, setNewTitle] = useState("");
  const [newStart, setNewStart] = useState("09:30");
  const [newEnd, setNewEnd] = useState("10:30");

  // Get active bookings for the selected resource and date
  const activeBookings = useMemo(() => {
    return bookings.filter(
      (b) => b.resource_id === selectedResource && b.date === selectedDate && b.status !== "Cancelled"
    );
  }, [bookings, selectedResource, selectedDate]);

  // Check if the current draft booking overlaps with any active bookings
  const draftConflict = useMemo(() => {
    if (!newStart || !newEnd || !isModalOpen) return false;
    const startOff = timeToOffset(newStart);
    const endOff = timeToOffset(newEnd);
    if (startOff >= endOff) return "Invalid time range"; // end before start

    for (const b of activeBookings) {
      const bStartOff = timeToOffset(b.start_time);
      const bEndOff = timeToOffset(b.end_time);
      if (checkOverlap(startOff, endOff, bStartOff, bEndOff)) {
        return true;
      }
    }
    return false;
  }, [newStart, newEnd, activeBookings, isModalOpen]);

  const handleBookSlot = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) {
      toast.error("Please provide a booking title.");
      return;
    }
    if (draftConflict) {
      toast.error("Time slot is unavailable due to an overlap.");
      return;
    }

    setIsSubmitting(true);
    await new Promise((r) => setTimeout(r, 600)); // simulate network
    
    const newBooking = {
      id: `b${Date.now()}`,
      resource_id: selectedResource,
      date: selectedDate,
      start_time: newStart,
      end_time: newEnd,
      booked_by: newTitle,
      status: "Upcoming",
    };
    
    setBookings([...bookings, newBooking]);
    toast.success("Booking confirmed! Reminder notification scheduled.");
    setIsModalOpen(false);
    setNewTitle("");
    setIsSubmitting(false);
  };

  const cancelBooking = (id) => {
    setBookings((prev) =>
      prev.map((b) => (b.id === id ? { ...b, status: "Cancelled" } : b))
    );
    toast.success("Booking cancelled.");
  };

  return (
    <div className={styles.container}>
      {/* ── Selectors ──────────────────────────────────────────────────────── */}
      <div className={styles.selectorRow}>
        <div className={styles.fieldGroup}>
          <span className={styles.fieldLabel}>Resource</span>
          <select
            className={styles.select}
            value={selectedResource}
            onChange={(e) => setSelectedResource(e.target.value)}
          >
            {MOCK_BOOKABLE_RESOURCES.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
        <div className={styles.fieldGroup}>
          <span className={styles.fieldLabel}>Date</span>
          <input
            className={styles.input}
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
      </div>

      {/* ── Timeline Calendar ──────────────────────────────────────────────── */}
      <div className={styles.timelineWrapper}>
        {/* Background hours grid */}
        {Array.from({ length: END_HOUR - START_HOUR + 1 }).map((_, i) => {
          const hour = START_HOUR + i;
          const displayHour = hour > 12 ? `${hour - 12}:00 PM` : `${hour}:00 AM`;
          return (
            <div key={hour} className={styles.timeSlot}>
              <span className={styles.timeLabel}>
                {hour === 12 ? "12:00 PM" : displayHour}
              </span>
            </div>
          );
        })}

        {/* Existing Bookings */}
        {activeBookings.map((b) => {
          const top = timeToOffset(b.start_time) * PIXELS_PER_MINUTE;
          const height = (timeToOffset(b.end_time) - timeToOffset(b.start_time)) * PIXELS_PER_MINUTE;
          return (
            <div
              key={b.id}
              className={`${styles.bookingBlock} ${styles.bookingBooked}`}
              style={{ top: `${top}px`, height: `${height}px` }}
            >
              <span className={styles.bookingTitle}>Booked - {b.booked_by}</span>
              <span>{b.start_time} to {b.end_time}</span>
            </div>
          );
        })}

        {/* Draft Conflict Visualizer (Only visible when modal is open) */}
        {isModalOpen && newStart && newEnd && (
          <div
            className={`${styles.bookingBlock} ${draftConflict ? styles.bookingConflict : styles.bookingBooked}`}
            style={{
              top: `${Math.max(0, timeToOffset(newStart) * PIXELS_PER_MINUTE)}px`,
              height: `${Math.max(10, (timeToOffset(newEnd) - timeToOffset(newStart)) * PIXELS_PER_MINUTE)}px`,
              opacity: draftConflict ? 1 : 0.5, // 50% opacity if it's fine, 100% if conflict
            }}
          >
            {draftConflict ? (
              <span style={{ fontWeight: 600 }}>Requested {newStart} to {newEnd} - conflict - slot is unavailable</span>
            ) : (
              <span style={{ fontWeight: 600 }}>Drafting {newStart} to {newEnd}</span>
            )}
          </div>
        )}
      </div>

      {/* ── Book Action ────────────────────────────────────────────────────── */}
      <div style={{ marginTop: "var(--space-4)" }}>
        <button className={styles.primaryBtn} onClick={() => setIsModalOpen(true)}>
          Book a slot
        </button>
      </div>

      {/* ── Your Bookings List ─────────────────────────────────────────────── */}
      <h3 style={{ marginTop: "var(--space-6)", fontSize: "1.125rem", color: "var(--color-text)", fontWeight: 600 }}>
        Agenda for {dayjs(selectedDate).format("MMM D, YYYY")}
      </h3>
      <div className={styles.bookingList}>
        {activeBookings.length > 0 ? (
          activeBookings.map((b) => (
            <div key={b.id} className={styles.bookingItem}>
              <div className={styles.bookingItemMeta}>
                <span className={styles.bookingItemTitle}>{b.booked_by}</span>
                <span className={styles.bookingItemTime}>{b.start_time} - {b.end_time}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
                <span className={`${styles.badge} ${STATUS_CLASS[b.status] || ""}`}>
                  {b.status}
                </span>
                {b.status === "Upcoming" && (
                  <button className={styles.actionLink} onClick={() => cancelBooking(b.id)}>
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))
        ) : (
          <p style={{ color: "var(--color-text-subtle)", fontSize: "0.9375rem" }}>
            No bookings on this date.
          </p>
        )}
      </div>

      {/* ── Booking Form Modal ─────────────────────────────────────────────── */}
      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalContent}>
            <span className={styles.modalTitle}>Book Resource</span>
            
            <form onSubmit={handleBookSlot} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
              <div className={styles.fieldGroup}>
                <label className={styles.fieldLabel}>Booking Title</label>
                <input
                  className={styles.input}
                  placeholder="e.g. Design Team Sync"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  autoFocus
                />
              </div>

              <div className={styles.twoCol}>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>Start Time</label>
                  <input
                    className={styles.input}
                    type="time"
                    value={newStart}
                    onChange={(e) => setNewStart(e.target.value)}
                  />
                </div>
                <div className={styles.fieldGroup}>
                  <label className={styles.fieldLabel}>End Time</label>
                  <input
                    className={styles.input}
                    type="time"
                    value={newEnd}
                    onChange={(e) => setNewEnd(e.target.value)}
                  />
                </div>
              </div>

              {draftConflict && draftConflict !== "Invalid time range" && (
                <div style={{ padding: "10px", backgroundColor: "rgba(239,68,68,0.1)", color: "var(--color-error)", borderRadius: "var(--radius-md)", fontSize: "0.875rem" }}>
                  <strong>Conflict:</strong> This slot overlaps with an existing booking. Please choose a different time.
                </div>
              )}

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
                  disabled={isSubmitting || !!draftConflict}
                >
                  {isSubmitting ? "Booking…" : "Confirm Booking"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
