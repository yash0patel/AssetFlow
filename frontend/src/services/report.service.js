/**
 * services/report.service.js
 * ──────────────────────────
 * API services for Analytics Reports.
 */

import api from "./api";

const reportService = {
  async getAssetUtilization() {
    const response = await api.get("/reports/asset-utilization");
    return response.data;
  },

  async getDepartmentAllocationSummary() {
    const response = await api.get("/reports/department-allocation-summary");
    return response.data;
  },

  async getMaintenanceFrequency() {
    const response = await api.get("/reports/maintenance-frequency");
    return response.data;
  },

  async getAssetsNearRetirement() {
    const response = await api.get("/reports/assets-near-retirement");
    return response.data;
  },
};

export default reportService;
