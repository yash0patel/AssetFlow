/**
 * services/notification.service.js
 * ───────────────────────────────
 * API services for notifications.
 */

import api from "./api";

const notificationService = {
  async listNotifications(params) {
    const response = await api.get("/notifications/", { params });
    return response.data;
  },

  async markRead(id) {
    const response = await api.post(`/notifications/${id}/read`);
    return response.data;
  },

  async markAllRead() {
    const response = await api.post("/notifications/read-all");
    return response.data;
  },
};

export default notificationService;
