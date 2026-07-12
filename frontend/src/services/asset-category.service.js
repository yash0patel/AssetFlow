/**
 * services/asset-category.service.js
 * ──────────────────────────────────
 * API services for Asset Category CRUD operations.
 */

import api from "./api";

const assetCategoryService = {
  async listCategories(params) {
    const response = await api.get("/asset-categories/", { params });
    return response.data;
  },

  async createCategory(data) {
    const response = await api.post("/asset-categories/", data);
    return response.data;
  },

  async getCategory(id) {
    const response = await api.get(`/asset-categories/${id}`);
    return response.data;
  },

  async updateCategory(id, data) {
    const response = await api.put(`/asset-categories/${id}`, data);
    return response.data;
  },

  async deleteCategory(id) {
    const response = await api.delete(`/asset-categories/${id}`);
    return response.data;
  },
};

export default assetCategoryService;
