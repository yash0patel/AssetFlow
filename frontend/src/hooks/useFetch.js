/**
 * hooks/useFetch.js
 * ──────────────────
 * Thin wrapper around TanStack Query's useQuery for simple GET requests.
 * For complex queries use useQuery directly with a service function.
 *
 * @example
 *   const { data, isLoading, error } = useFetch(["departments"], fetchDepartments);
 */

import { useQuery } from "@tanstack/react-query";

export function useFetch(queryKey, fetchFn, options = {}) {
  return useQuery({
    queryKey,
    queryFn: fetchFn,
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
}
