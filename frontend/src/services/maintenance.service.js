/**
 * services/maintenance.service.js
 * ───────────────────────────────
 * API services for Maintenance Kanban Board.
 */

import api from "./api";

const maintenanceService = {
  async listMaintenanceRequests(params) {
    const response = await api.get("/maintenance/", { params });
    return response.data;
  },

  async listTechnicians() {
    const response = await api.get("/maintenance/technicians");
    return response.data;
  },

  async raiseRequest(data) {
    const response = await api.post("/maintenance/", data);
    return response.data;
  },

  async getRequest(id) {
    const response = await api.get(`/maintenance/${id}`);
    return response.data;
  },

  async approveRequest(id, data) {
    const response = await api.post(`/maintenance/${id}/approve`, data);
    return response.data;
  },

  async rejectRequest(id, data) {
    const response = await api.post(`/maintenance/${id}/reject`, data);
    return response.data;
  },

  async assignRequest(id, data) {
    const response = await api.post(`/maintenance/${id}/assign`, data);
    return response.data;
  },

  async startRequest(id) {
    const response = await api.post(`/maintenance/${id}/start`);
    return response.data;
  },

  async resolveRequest(id, data) {
    const response = await api.post(`/maintenance/${id}/resolve`, data);
    return response.data;
  },
};

export default maintenanceService;
