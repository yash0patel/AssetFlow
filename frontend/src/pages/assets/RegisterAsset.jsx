/**
 * pages/assets/RegisterAsset.jsx
 * ─────────────────────────────
 * Screen 4B: Register a new asset.
 * All fields align with the backend Asset model.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { ROUTES } from "@routes/routeConstants";
import {
  MOCK_ASSETS,
  MOCK_CATEGORIES,
  MOCK_CONDITIONS,
  MOCK_LOCATIONS,
  MOCK_DEPARTMENTS,
  generateAssetTag,
} from "./mockAssets";
import styles from "./asset.module.css";

// ── Validation schema ──────────────────────────────────────────────────────────
const registerSchema = z.object({
  name:             z.string().min(2, "Name is required"),
  category:         z.string().min(1, "Category is required"),
  serial_number:    z.string().optional(),
  acquisition_date: z.string().optional(),
  acquisition_cost: z.string().optional(),
  condition:        z.string().min(1, "Condition is required"),
  location:         z.string().min(1, "Location is required"),
  department:       z.string().optional(),
  description:      z.string().optional(),
  is_bookable:      z.boolean().optional(),
});

export default function RegisterAsset() {
  const navigate    = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Auto-generate asset tag based on current mock data
  const nextTag = generateAssetTag(MOCK_ASSETS);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: { condition: "Good", is_bookable: false },
  });

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    // Simulate async save
    await new Promise((r) => setTimeout(r, 600));
    toast.success(`Asset ${nextTag} registered successfully!`);
    setIsSubmitting(false);
    navigate(ROUTES.ASSETS);
  };

  return (
    <div className={styles.container}>
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className={styles.pageHeader}>
        <button className={styles.backBtn} onClick={() => navigate(ROUTES.ASSETS)}>
          ← Back
        </button>
        <h1 className={styles.pageTitle}>Register New Asset</h1>
      </div>

      <div className={styles.formCard}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className={styles.formGrid}>

            {/* Auto-generated Asset Tag — read only */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Asset Tag (auto-generated)</label>
              <input className={styles.input} value={nextTag} disabled readOnly />
            </div>

            {/* Name */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Asset Name *</label>
              <input
                className={`${styles.input} ${errors.name ? styles.inputError : ""}`}
                placeholder="e.g. Dell Laptop"
                {...register("name")}
              />
              {errors.name && <span className={styles.errorText}>{errors.name.message}</span>}
            </div>

            {/* Category */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Category *</label>
              <select
                className={`${styles.select} ${errors.category ? styles.inputError : ""}`}
                {...register("category")}
              >
                <option value="">Select category…</option>
                {MOCK_CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              {errors.category && <span className={styles.errorText}>{errors.category.message}</span>}
            </div>

            {/* Serial Number */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Serial Number</label>
              <input
                className={styles.input}
                placeholder="e.g. SN-0012345"
                {...register("serial_number")}
              />
            </div>

            {/* Acquisition Date */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Acquisition Date</label>
              <input
                className={styles.input}
                type="date"
                {...register("acquisition_date")}
              />
            </div>

            {/* Acquisition Cost */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Acquisition Cost (₹)</label>
              <input
                className={styles.input}
                type="number"
                min="0"
                placeholder="e.g. 68000"
                {...register("acquisition_cost")}
              />
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-subtle)" }}>
                For reporting only — not linked to accounting.
              </span>
            </div>

            {/* Condition */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Condition *</label>
              <select
                className={`${styles.select} ${errors.condition ? styles.inputError : ""}`}
                {...register("condition")}
              >
                {MOCK_CONDITIONS.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              {errors.condition && <span className={styles.errorText}>{errors.condition.message}</span>}
            </div>

            {/* Location */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Location *</label>
              <select
                className={`${styles.select} ${errors.location ? styles.inputError : ""}`}
                {...register("location")}
              >
                <option value="">Select location…</option>
                {MOCK_LOCATIONS.map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
              {errors.location && <span className={styles.errorText}>{errors.location.message}</span>}
            </div>

            {/* Department */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Owning Department</label>
              <select className={styles.select} {...register("department")}>
                <option value="">Select department…</option>
                {MOCK_DEPARTMENTS.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* Description */}
            <div className={`${styles.fieldGroup} ${styles.formGridFull}`}>
              <label className={styles.label}>Description</label>
              <textarea
                className={styles.textarea}
                placeholder="Optional notes about this asset…"
                {...register("description")}
              />
            </div>

            {/* Bookable flag */}
            <div className={`${styles.fieldGroup} ${styles.formGridFull}`}>
              <label className={styles.checkRow}>
                <input type="checkbox" {...register("is_bookable")} />
                <span className={styles.label}>Shared / Bookable asset</span>
              </label>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-subtle)", marginTop: "4px" }}>
                Enable to allow employees to book this asset via Resource Booking.
              </span>
            </div>
          </div>

          {/* ── Form Actions ───────────────────────────────────────────────── */}
          <div className={styles.formActions}>
            <button
              type="button"
              className={styles.cancelBtn}
              onClick={() => navigate(ROUTES.ASSETS)}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={styles.submitBtn}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Registering…" : "Register Asset"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
