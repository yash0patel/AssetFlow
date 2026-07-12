/**
 * services/booking.service.js
 * ───────────────────────────
 * API services for Resource Booking.
 */

import api from "./api";

const bookingService = {
  async listBookings(params) {
    const response = await api.get("/bookings/", { params });
    return response.data;
  },

  async createBooking(data) {
    const response = await api.post("/bookings/", data);
    return response.data;
  },

  async cancelBooking(id, data) {
    const response = await api.post(`/bookings/${id}/cancel`, data);
    return response.data;
  },
};

export default bookingService;
