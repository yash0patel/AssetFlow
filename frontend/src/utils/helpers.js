/**
 * utils/helpers.js
 * ─────────────────
 * Miscellaneous utility functions.
 */

import { clsx } from "clsx";

/**
 * Merge class names conditionally (thin wrapper around clsx).
 * @example cn("base", isActive && "active", {"disabled": !enabled})
 */
export const cn = (...inputs) => clsx(...inputs);

/** Extract an error message from an Axios error response or plain Error. */
export const getErrorMessage = (error) => {
  return (
    error?.response?.data?.message ||
    error?.response?.data?.detail ||
    error?.message ||
    "An unexpected error occurred."
  );
};

/** Return the initials for a display name (up to 2 letters). */
export const getInitials = (name = "") =>
  name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase())
    .join("");

/** Deep-clone a plain object/array via JSON round-trip. */
export const deepClone = (obj) => JSON.parse(JSON.stringify(obj));

/** Check if a value is empty (null, undefined, empty string/array/object). */
export const isEmpty = (value) => {
  if (value === null || value === undefined) return true;
  if (typeof value === "string") return value.trim() === "";
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") return Object.keys(value).length === 0;
  return false;
};
