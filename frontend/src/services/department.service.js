/**
 * services/department.service.js
 * ──────────────────────────────
 * API services for Department CRUD operations.
 */

import api from "./api";

const departmentService = {
  async listDepartments(params) {
    const response = await api.get("/departments/", { params });
    return response.data;
  },

  async createDepartment(data) {
    const response = await api.post("/departments/", data);
    return response.data;
  },

  async getDepartment(id) {
    const response = await api.get(`/departments/${id}`);
    return response.data;
  },

  async updateDepartment(id, data) {
    const response = await api.put(`/departments/${id}`, data);
    return response.data;
  },

  async deleteDepartment(id) {
    const response = await api.delete(`/departments/${id}`);
    return response.data;
  },
};

export default departmentService;
