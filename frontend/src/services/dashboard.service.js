/**
 * services/dashboard.service.js
 * ─────────────────────────────
 * API services for Dashboard data.
 */

import api from "./api";

const dashboardService = {
  async getKpis() {
    const response = await api.get("/dashboard/kpis");
    return response.data;
  },

  async getOverdueAllocations() {
    const response = await api.get("/dashboard/overdue-allocations");
    return response.data;
  },

  async getRecentActivity() {
    const response = await api.get("/dashboard/recent-activity");
    return response.data;
  },
};

export default dashboardService;
