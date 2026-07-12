/**
 * utils/formatters.js
 * ────────────────────
 * Display-layer formatting helpers using dayjs.
 */

import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { DATE_FORMAT, DATETIME_FORMAT } from "./constants";

dayjs.extend(relativeTime);

/** Format a date string or Date object to "DD MMM YYYY". */
export const formatDate = (value) => (value ? dayjs(value).format(DATE_FORMAT) : "—");

/** Format a date to "DD MMM YYYY, HH:mm". */
export const formatDateTime = (value) =>
  value ? dayjs(value).format(DATETIME_FORMAT) : "—";

/** Return a human-readable relative time, e.g. "3 hours ago". */
export const timeAgo = (value) => (value ? dayjs(value).fromNow() : "—");

/** Format a number as a currency string. */
export const formatCurrency = (amount, currency = "INR") =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency }).format(amount ?? 0);

/** Capitalise the first letter of a string. */
export const capitalise = (str = "") =>
  str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();

/** Convert a snake_case or SCREAMING_CASE string to Title Case. */
export const enumToLabel = (value = "") =>
  value
    .toLowerCase()
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");

/** Truncate a string to maxLength and append an ellipsis. */
export const truncate = (str = "", maxLength = 50) =>
  str.length > maxLength ? `${str.slice(0, maxLength)}…` : str;
