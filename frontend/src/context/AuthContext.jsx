/**
 * context/AuthContext.jsx
 * ────────────────────────
 * Provides authentication state to the entire React tree.
 * Consuming components should use the useAuth() hook.
 */

import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import authService from "../services/auth.service";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount — restore session from localStorage
  useEffect(() => {
    async function restoreSession() {
      const token = localStorage.getItem("access_token");
      if (token) {
        try {
          const profile = await authService.getMe();
          setUser(profile);
        } catch (err) {
          // Access token stale — try refreshing before giving up
          const rToken = localStorage.getItem("refresh_token");
          if (rToken) {
            try {
              const newAccessToken = await authService.refreshToken();
              if (newAccessToken) {
                const profile = await authService.getMe();
                setUser(profile);
              }
            } catch (_refreshErr) {
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
            }
          } else {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
          }
        }
      }
      setIsLoading(false);
    }
    restoreSession();
  }, []);

  const login = useCallback((userData, token, refreshToken) => {
    localStorage.setItem("access_token", token);
    if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
    setUser(userData);
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (err) {
      console.error("Logout failed on backend, clearing local storage:", err);
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
    }),
    [user, isLoading, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
