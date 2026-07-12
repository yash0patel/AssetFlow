/**
 * services/activity-log.service.js
 * ────────────────────────────────
 * API services for Activity Logs.
 */

import api from "./api";

const activityLogService = {
  async listActivityLogs(params) {
    const response = await api.get("/activity-logs/", { params });
    return response.data;
  },
};

export default activityLogService;
