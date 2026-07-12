/**
 * services/audit.service.js
 * ─────────────────────────
 * API services for Asset Audits.
 */

import api from "./api";

const auditService = {
  async listCycles(params) {
    const response = await api.get("/audits/", { params });
    return response.data;
  },

  async createCycle(data) {
    const response = await api.post("/audits/", data);
    return response.data;
  },

  async getCycle(id) {
    const response = await api.get(`/audits/${id}`);
    return response.data;
  },

  async getCycleItems(id) {
    const response = await api.get(`/audits/${id}/items`);
    return response.data;
  },

  async verifyItem(cycleId, itemId, data) {
    const response = await api.post(`/audits/${cycleId}/items/${itemId}/verify`, data);
    return response.data;
  },

  async closeCycle(id) {
    const response = await api.post(`/audits/${id}/close`);
    return response.data;
  },
};

export default auditService;
