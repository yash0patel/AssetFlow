/**
 * services/asset.service.js
 * ─────────────────────────
 * API services for Asset Directory and Registration.
 */

import api from "./api";

const assetService = {
  async listAssets(params) {
    const response = await api.get("/assets/", { params });
    return response.data;
  },

  async registerAsset(data) {
    const response = await api.post("/assets/", data);
    return response.data;
  },

  async getAsset(id) {
    const response = await api.get(`/assets/${id}`);
    return response.data;
  },

  async updateAsset(id, data) {
    const response = await api.patch(`/assets/${id}`, data);
    return response.data;
  },

  async listLocations() {
    const response = await api.get("/assets/locations");
    return response.data;
  },

  async listBookableAssets() {
    const response = await api.get("/assets/bookable");
    return response.data;
  },
};

export default assetService;
