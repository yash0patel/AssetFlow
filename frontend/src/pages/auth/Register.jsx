/**
 * pages/auth/Register.jsx
 * ────────────────────────
 * Employee account creation form.
 * No role selection — Admin assigns roles from Employee Directory.
 * Uses mock signup — replace with real API call when backend is ready.
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
import styles from "./register.module.css";

// ── Validation schema ──────────────────────────────────────────────────────────
const registerSchema = z
  .object({
    fullName: z
      .string()
      .min(2, "Full name must be at least 2 characters")
      .max(80, "Full name is too long"),
    email: z.string().email("Enter a valid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

// ── Component ──────────────────────────────────────────────────────────────────
export default function Register() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(registerSchema) });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      const response = await authService.register(data.fullName, data.email, data.password);
      const { user, access_token, refresh_token } = response;
      login(user, access_token, refresh_token);
      toast.success("Account created! Welcome to AssetFlow.");
      navigate(ROUTES.DASHBOARD, { replace: true });
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Registration failed. Please try again.";
      toast.error(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        {/* Header */}
        <div className={styles.cardHeader}>AssetFlow – create account</div>

        <div className={styles.cardBody}>
          {/* Avatar */}
          <div className={styles.avatar}>AF</div>

          {/* Role badge — clarifies no role selection */}
          <span className={styles.roleBadge}>Employee account</span>

          {/* Registration form */}
          <form className={styles.form} onSubmit={handleSubmit(onSubmit)} noValidate>
            {/* Full Name */}
            <div className={styles.fieldGroup}>
              <label htmlFor="fullName" className={styles.label}>
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                placeholder="Jane Doe"
                autoComplete="name"
                className={`${styles.input} ${errors.fullName ? styles.inputError : ""}`}
                {...register("fullName")}
              />
              {errors.fullName && (
                <span className={styles.errorText}>{errors.fullName.message}</span>
              )}
            </div>

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
                placeholder="Min. 8 characters"
                autoComplete="new-password"
                className={`${styles.input} ${errors.password ? styles.inputError : ""}`}
                {...register("password")}
              />
              {errors.password && (
                <span className={styles.errorText}>{errors.password.message}</span>
              )}
            </div>

            {/* Confirm Password */}
            <div className={styles.fieldGroup}>
              <label htmlFor="confirmPassword" className={styles.label}>
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                placeholder="Re-enter password"
                autoComplete="new-password"
                className={`${styles.input} ${errors.confirmPassword ? styles.inputError : ""}`}
                {...register("confirmPassword")}
              />
              {errors.confirmPassword && (
                <span className={styles.errorText}>{errors.confirmPassword.message}</span>
              )}
            </div>

            {/* Submit */}
            <button
              id="register-submit"
              type="submit"
              className={styles.submitBtn}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Creating account…" : "Create Account"}
            </button>
          </form>

          {/* Divider */}
          <div className={styles.divider} />

          {/* Back to login */}
          <div className={styles.backRow}>
            <Link to={ROUTES.LOGIN} className={styles.backLink}>
              Already have an account? Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
