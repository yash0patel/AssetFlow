/**
 * services/employee.service.js
 * ───────────────────────────
 * API services for Employee CRUD and promotion operations.
 */

import api from "./api";

const employeeService = {
  async listEmployees(params) {
    const response = await api.get("/employees/", { params });
    return response.data;
  },

  async createEmployee(data) {
    const response = await api.post("/employees/", data);
    return response.data;
  },

  async getEmployee(id) {
    const response = await api.get(`/employees/${id}`);
    return response.data;
  },

  async updateEmployee(id, data) {
    const response = await api.put(`/employees/${id}`, data);
    return response.data;
  },

  async listUsersWithoutEmployee() {
    const response = await api.get("/employees/users-without-employee");
    return response.data;
  },

  async promoteEmployee(id, data) {
    const response = await api.post(`/employees/${id}/promote`, data);
    return response.data;
  },

  async demoteEmployee(id) {
    const response = await api.post(`/employees/${id}/demote`);
    return response.data;
  },
};

export default employeeService;
