/**
 * services/allocation.service.js
 * ──────────────────────────────
 * API services for Allocations and Transfers.
 */

import api from "./api";

const allocationService = {
  async listAllocations(params) {
    const response = await api.get("/allocations/", { params });
    return response.data;
  },

  async allocateAsset(data) {
    const response = await api.post("/allocations/", data);
    return response.data;
  },

  async returnAsset(id, data) {
    const response = await api.post(`/allocations/${id}/return`, data);
    return response.data;
  },

  async createTransferRequest(allocationId, data) {
    const response = await api.post(`/allocations/${allocationId}/transfer-request`, data);
    return response.data;
  },

  async listTransfers(params) {
    const response = await api.get("/allocations/transfers", { params });
    return response.data;
  },

  async approveTransfer(transferId) {
    const response = await api.post(`/allocations/transfers/${transferId}/approve`);
    return response.data;
  },

  async rejectTransfer(transferId, data) {
    const response = await api.post(`/allocations/transfers/${transferId}/reject`, data);
    return response.data;
  },
};

export default allocationService;
