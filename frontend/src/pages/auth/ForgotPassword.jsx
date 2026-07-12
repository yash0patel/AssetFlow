/**
 * pages/auth/ForgotPassword.jsx
 * ──────────────────────────────
 * Two-state page:
 *   1. Email input → user submits their email
 *   2. Success state → instructs user to check their inbox
 *
 * Mock only — replace with real API call when backend is ready.
 */

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

import { ROUTES } from "@routes/routeConstants";
import styles from "./forgot-password.module.css";

// ── Validation schema ──────────────────────────────────────────────────────────
const forgotSchema = z.object({
  email: z.string().email("Enter a valid email address"),
});

// ── Mock send reset link ───────────────────────────────────────────────────────
function mockSendResetLink(email) {
  // Simulate a network delay and always succeed
  return new Promise((resolve) => setTimeout(() => resolve({ email }), 800));
}

// ── Component ──────────────────────────────────────────────────────────────────
export default function ForgotPassword() {
  const [sentTo, setSentTo] = useState(null); // null = form state, string = success state
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(forgotSchema) });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      await mockSendResetLink(data.email);
      setSentTo(data.email);
      toast.success("Reset link sent!");
    } catch {
      toast.error("Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        {/* Header */}
        <div className={styles.cardHeader}>AssetFlow – reset password</div>

        <div className={styles.cardBody}>
          {sentTo ? (
            /* ── Success state ── */
            <div className={styles.successBox}>
              <div className={styles.successIcon}>✉️</div>

              <p className={styles.successTitle}>Check your inbox</p>

              <p className={styles.successText}>
                We sent a password reset link to{" "}
                <span className={styles.successEmail}>{sentTo}</span>.
                <br />
                Check your spam folder if you don't see it.
              </p>

              <div className={styles.divider} style={{ width: "100%" }} />

              <div className={styles.backRow}>
                <Link to={ROUTES.LOGIN} className={styles.backLink}>
                  Back to Sign In
                </Link>
              </div>
            </div>
          ) : (
            /* ── Form state ── */
            <>
              {/* Avatar */}
              <div className={styles.avatar}>AF</div>

              <p className={styles.hint}>
                Enter your email and we'll send you a link to reset your password.
              </p>

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

                {/* Submit */}
                <button
                  id="forgot-password-submit"
                  type="submit"
                  className={styles.submitBtn}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Sending…" : "Send Reset Link"}
                </button>
              </form>

              {/* Divider */}
              <div className={styles.divider} />

              {/* Back to login */}
              <div className={styles.backRow}>
                <Link to={ROUTES.LOGIN} className={styles.backLink}>
                  Back to Sign In
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
