/**
 * pages/auth/Login.jsx
 * ─────────────────────
 * Login form with email/password validation.
 * Uses mock credentials — replace with real API call when backend is ready.
 */

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { useAuth } from "@hooks/useAuth";
import { ROUTES } from "@routes/routeConstants";
import authService from "../../services/auth.service";
import styles from "./login.module.css";

// ── Validation schema ──────────────────────────────────────────────────────────
const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

// ── Component ──────────────────────────────────────────────────────────────────
export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      const response = await authService.login(data.email, data.password);
      const { user, access_token, refresh_token } = response;
      login(user, access_token, refresh_token);
      toast.success(`Welcome back, ${user.name.split(" ")[0]}!`);
      navigate(ROUTES.DASHBOARD, { replace: true });
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Invalid email or password";
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        {/* Header */}
        <div className={styles.cardHeader}>AssetFlow – login</div>

        <div className={styles.cardBody}>
          {/* Avatar */}
          <div className={styles.avatar}>AF</div>

          {/* Login form */}
          <form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
            {/* Email */}
            <div className={styles.fieldGroup}>
              <label htmlFor="email" className={styles.label}>
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="name@company.com"
                autoComplete="email"
                className={`${styles.input} ${errors.email ? styles.inputError : ""}`}
                {...register("email")}
              />
              {errors.email && (
                <span className={styles.errorText}>{errors.email.message}</span>
              )}
            </div>

            {/* Password */}
            <div className={styles.fieldGroup}>
              <label htmlFor="password" className={styles.label}>
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder="••••••••••"
                autoComplete="current-password"
                className={`${styles.input} ${errors.password ? styles.inputError : ""}`}
                {...register("password")}
              />
              {errors.password && (
                <span className={styles.errorText}>{errors.password.message}</span>
              )}
            </div>

            {/* Forgot password */}
            <div className={styles.forgotRow}>
              <Link to={ROUTES.FORGOT_PASSWORD} className={styles.forgotLink}>
                Forgot password
              </Link>
            </div>

            {/* Submit */}
            <button
              id="login-submit"
              type="submit"
              className={styles.submitBtn}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Signing in…" : "Sign In"}
            </button>
          </form>

          {/* Divider */}
          <div className={styles.divider} />

          {/* Signup section */}
          <div className={styles.signupSection}>
            <span className={styles.signupLabel}>New here?</span>

            <div className={styles.signupInfo}>
              Sign up creates an employee account.{" "}
              <span className={styles.signupInfoAccent}>Admin</span> roles assigned later.
            </div>

            <Link to={ROUTES.REGISTER} id="create-account-link">
              <button id="create-account-btn" className={styles.createBtn} type="button">
                Create Account
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
