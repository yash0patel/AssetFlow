/**
 * services/auth.service.js
 * ────────────────────────
 * Client service layer for login, registration, password recovery,
 * and token refreshes interacting with the backend FastAPI authentication.
 */

import api from "./api";

const authService = {
  /**
   * Log in user using email and password.
   */
  async login(email, password) {
    const response = await api.post("/auth/login", { email, password });
    return response.data;
  },

  /**
   * Register a new employee account.
   */
  async register(fullName, email, password) {
    const response = await api.post("/auth/register", { fullName, email, password });
    return response.data;
  },

  /**
   * Revoke active backend session and sign user out.
   */
  async logout() {
    try {
      const response = await api.post("/auth/logout");
      return response.data;
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },

  /**
   * Get currently authenticated user details.
   */
  async getMe() {
    const response = await api.get("/auth/me", { skipInterceptor: true });
    return response.data;
  },

  /**
   * Use refresh token to obtain a fresh access token from the backend.
   */
  async refreshToken() {
    const rToken = localStorage.getItem("refresh_token");
    if (!rToken) return null;

    try {
      const response = await api.post("/auth/refresh", { refresh_token: rToken }, { skipInterceptor: true });
      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      localStorage.setItem("access_token", access_token);
      if (newRefreshToken) {
        localStorage.setItem("refresh_token", newRefreshToken);
      }
      return access_token;
    } catch (error) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      throw error;
    }
  },

  /**
   * Send password reset request email link.
   */
  async forgotPassword(email) {
    const response = await api.post("/auth/forgot-password", { email });
    return response.data;
  },
};

export default authService;
