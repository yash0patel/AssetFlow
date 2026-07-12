/**
 * hooks/usePagination.js
 * ───────────────────────
 * Client-side pagination state manager.
 * Pairs naturally with TanStack Query's keepPreviousData option.
 *
 * @example
 *   const { page, pageSize, goToPage, nextPage, prevPage } = usePagination();
 */

import { useState } from "react";

export function usePagination(initialPage = 1, initialPageSize = 20) {
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);

  const nextPage = () => setPage((p) => p + 1);
  const prevPage = () => setPage((p) => Math.max(1, p - 1));
  const goToPage = (n) => setPage(Math.max(1, n));
  const reset = () => setPage(initialPage);

  return { page, pageSize, setPageSize, nextPage, prevPage, goToPage, reset };
}
