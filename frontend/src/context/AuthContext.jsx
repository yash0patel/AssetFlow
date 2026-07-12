/**
 * context/AuthContext.jsx
 * ────────────────────────
 * Provides authentication state to the entire React tree.
 * Consuming components should use the useAuth() hook.
 */

import { createContext, useCallback, useEffect, useMemo, useState } from "react";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // On mount — restore session from localStorage
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      // TODO: validate token and fetch /me in business-logic phase
      // const profile = await authService.getMe();
      // setUser(profile);
    }
    setIsLoading(false);
  }, []);

  const login = useCallback((userData, token, refreshToken) => {
    localStorage.setItem("access_token", token);
    if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
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
