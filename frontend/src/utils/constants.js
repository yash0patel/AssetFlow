/**
 * utils/constants.js
 * ───────────────────
 * Frontend application-level constants.
 */

export const APP_NAME = import.meta.env.VITE_APP_NAME || "AssetFlow";
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8001/api/v1";

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// Local-storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: "access_token",
  REFRESH_TOKEN: "refresh_token",
  THEME: "assetflow_theme",
  USER: "assetflow_user",
};

// Date format strings (dayjs)
export const DATE_FORMAT = "DD MMM YYYY";
export const DATETIME_FORMAT = "DD MMM YYYY, HH:mm";

// Asset statuses (mirror backend enums)
export const ASSET_STATUS = {
  AVAILABLE: "available",
  ALLOCATED: "allocated",
  UNDER_MAINTENANCE: "under_maintenance",
  RETIRED: "retired",
  LOST: "lost",
  DISPOSED: "disposed",
};

// User roles (mirror backend enums)
export const USER_ROLES = {
  ADMIN: "admin",
  ASSET_MANAGER: "asset_manager",
  DEPARTMENT_HEAD: "department_head",
  EMPLOYEE: "employee",
};
