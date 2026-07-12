/**
 * context/NotificationContext.jsx
 * ─────────────────────────────────
 * Wraps react-hot-toast for programmatic notifications across the app.
 * Components call useNotification() to trigger toasts.
 */

import { createContext, useCallback, useMemo } from "react";
import toast from "react-hot-toast";

export const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const success = useCallback((message) => toast.success(message), []);
  const error = useCallback((message) => toast.error(message), []);
  const info = useCallback((message) => toast(message, { icon: "ℹ️" }), []);
  const warn = useCallback(
    (message) => toast(message, { icon: "⚠️", style: { background: "#FEF3C7" } }),
    []
  );
  const dismiss = useCallback((id) => toast.dismiss(id), []);

  const value = useMemo(
    () => ({ success, error, info, warn, dismiss }),
    [success, error, info, warn, dismiss]
  );

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}
