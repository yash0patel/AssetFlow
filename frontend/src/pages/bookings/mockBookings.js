/**
 * pages/bookings/mockBookings.js
 * ──────────────────────────────
 * Mock data for Resource Booking screen.
 */

export const MOCK_BOOKABLE_RESOURCES = [
  { id: "r1", name: "Conference room B2", type: "Room" },
  { id: "r2", name: "Projector AF-0062", type: "Equipment" },
  { id: "r3", name: "Toyota Innova AF-0305", type: "Vehicle" },
];

export const MOCK_BOOKINGS = [
  {
    id: "b1",
    resource_id: "r1",
    date: "2026-07-07",
    start_time: "09:00",
    end_time: "10:00",
    booked_by: "Procurement Team",
    status: "Upcoming",
  },
  {
    id: "b2",
    resource_id: "r1",
    date: "2026-07-07",
    start_time: "14:00",
    end_time: "16:00",
    booked_by: "HR Orientation",
    status: "Upcoming",
  },
  {
    id: "b3",
    resource_id: "r2",
    date: "2026-07-07",
    start_time: "10:30",
    end_time: "12:00",
    booked_by: "Design Team",
    status: "Ongoing",
  },
];
