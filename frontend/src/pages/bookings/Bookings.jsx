/**
 * pages/bookings/Bookings.jsx
 * ────────────────────────────
 * Screen 6: Resource Booking Screen.
 */

import { useState, useMemo, useEffect, useRef } from "react";
import toast from "react-hot-toast";
import dayjs from "dayjs";
import assetService from "@services/asset.service";
import bookingService from "@services/booking.service";
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
  if (!timeStr) return 0;
  const [h, m] = timeStr.split(":").map(Number);
  return (h - START_HOUR) * 60 + m;
}

// Check if two time ranges overlap (Exclusive of boundaries, so 10:00-11:00 and 11:00-12:00 do NOT overlap)
function checkOverlap(s1, e1, s2, e2) {
  return s1 < e2 && s2 < e1;
}

export default function Bookings() {
  const [resources, setResources] = useState([]);
  const [selectedResource, setSelectedResource] = useState("");
  // Default to today's date
  const [selectedDate, setSelectedDate] = useState(dayjs().format("YYYY-MM-DD")); 
  
  const [bookings, setBookings] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // New Booking State
  const [newTitle, setNewTitle] = useState("");
  const [newStart, setNewStart] = useState("09:30");
  const [newEnd, setNewEnd] = useState("10:30");

  const isFirstMount = useRef(true);

  // Load resources and initial bookings
  useEffect(() => {
    async function initBookings() {
      setLoading(true);
      try {
        const assets = await assetService.listBookableAssets();
        setResources(assets);
        if (assets.length > 0) {
          const firstId = assets[0].id;
          setSelectedResource(firstId);
          const data = await bookingService.listBookings({ asset_id: firstId });
          setBookings(data.items || []);
        }
      } catch (err) {
        console.error("Error loading resources/bookings:", err);
      } finally {
        setLoading(false);
      }
    }
    initBookings();
  }, []);

  // Load bookings for selected resource (only on change after first mount)
  const loadBookings = async (resId) => {
    const id = resId || selectedResource;
    if (!id) return;
    setLoading(true);
    try {
      const data = await bookingService.listBookings({ asset_id: id });
      setBookings(data.items || []);
    } catch (err) {
      console.error("Error loading bookings:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isFirstMount.current) {
      isFirstMount.current = false;
      return;
    }
    if (selectedResource) {
      loadBookings(selectedResource);
    }
  }, [selectedResource]);

  // Get active bookings for the selected resource and date
  const activeBookings = useMemo(() => {
    return bookings.filter((b) => {
      const isSameDate = dayjs(b.start_datetime).format("YYYY-MM-DD") === selectedDate;
      return isSameDate && b.status !== "Cancelled";
    }).map(b => {
      const start = dayjs(b.start_datetime).format("HH:mm");
      const end = dayjs(b.end_datetime).format("HH:mm");
      return {
        ...b,
        start_time: start,
        end_time: end,
        booked_by: b.booked_by_name || "Employee",
      };
    });
  }, [bookings, selectedDate]);

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
      toast.error("Please provide a booking purpose/title.");
      return;
    }
    if (draftConflict) {
      toast.error("Time slot is unavailable due to an overlap.");
      return;
    }

    setIsSubmitting(true);
    try {
      const start_datetime = dayjs(`${selectedDate}T${newStart}:00`).toISOString();
      const end_datetime = dayjs(`${selectedDate}T${newEnd}:00`).toISOString();

      await bookingService.createBooking({
        asset_id: selectedResource,
        start_datetime,
        end_datetime,
        purpose: newTitle,
      });

      toast.success("Booking confirmed! Reminder notification scheduled.");
      setIsModalOpen(false);
      setNewTitle("");
      await loadBookings();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create booking.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelBooking = async (id) => {
    if (!window.confirm("Are you sure you want to cancel this booking?")) return;
    try {
      await bookingService.cancelBooking(id, { cancellation_reason: "User cancelled" });
      toast.success("Booking cancelled.");
      await loadBookings();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to cancel booking.");
    }
  };

  if (loading && resources.length === 0) {
    return <div className={styles.container}>Loading resources...</div>;
  }

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
            {resources.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} ({r.category_name})
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
              <span className={styles.bookingTitle}>{b.purpose || "Booked"} - {b.booked_by}</span>
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
              opacity: draftConflict ? 1 : 0.5,
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
        <button className={styles.primaryBtn} onClick={() => setIsModalOpen(true)} disabled={resources.length === 0}>
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
                <span className={styles.bookingItemTitle}>{b.purpose || "Booked"} by {b.booked_by}</span>
                <span className={styles.bookingItemTime}>{b.start_time} - {b.end_time}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
                <span className={`${styles.badge} ${STATUS_CLASS[b.status] || ""}`}>
                  {b.status}
                </span>
                {b.status === "Upcoming" && (
                  <button className={styles.actionLink} onClick={() => handleCancelBooking(b.id)}>
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
                <label className={styles.fieldLabel}>Booking Title/Purpose</label>
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
