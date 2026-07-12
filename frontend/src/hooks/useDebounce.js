/**
 * hooks/useDebounce.js
 * ─────────────────────
 * Debounces a rapidly-changing value.
 *
 * @param {*}      value - The value to debounce
 * @param {number} delay - Delay in milliseconds (default 300ms)
 * @returns The debounced value
 *
 * @example
 *   const debouncedSearch = useDebounce(searchTerm, 400);
 */

import { useEffect, useState } from "react";

export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
