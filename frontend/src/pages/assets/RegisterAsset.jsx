/**
 * pages/assets/RegisterAsset.jsx
 * ─────────────────────────────
 * Screen 4B: Register a new asset.
 * All fields align with the backend Asset model.
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { ROUTES } from "@routes/routeConstants";
import assetService from "@services/asset.service";
import assetCategoryService from "@services/asset-category.service";
import departmentService from "@services/department.service";
import styles from "./asset.module.css";

const CONDITIONS = ["New", "Good", "Fair", "Poor", "Damaged"];

// ── Validation schema ──────────────────────────────────────────────────────────
const registerSchema = z.object({
  name:             z.string().min(2, "Name is required"),
  category_id:      z.string().min(1, "Category is required"),
  serial_number:    z.string().optional(),
  acquisition_date: z.string().optional(),
  acquisition_cost: z.string().optional(),
  condition:        z.string().min(1, "Condition is required"),
  location_id:      z.string().min(1, "Location is required"),
  department_id:    z.string().optional(),
  description:      z.string().optional(),
  is_bookable:      z.boolean().optional(),
});

export default function RegisterAsset() {
  const navigate    = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [categories, setCategories] = useState([]);
  const [locations, setLocations] = useState([]);
  const [departments, setDepartments] = useState([]);

  useEffect(() => {
    async function loadFormOptions() {
      try {
        const [catData, locData, deptData] = await Promise.all([
          assetCategoryService.listCategories(),
          assetService.listLocations(),
          departmentService.listDepartments(),
        ]);
        setCategories(catData.items || catData);
        setLocations(locData);
        setDepartments(deptData.items || deptData);
      } catch (err) {
        console.error("Error loading register asset form options:", err);
      }
    }
    loadFormOptions();
  }, []);

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
    try {
      const payload = {
        ...data,
        serial_number: data.serial_number || null,
        acquisition_date: data.acquisition_date || null,
        acquisition_cost: data.acquisition_cost ? parseFloat(data.acquisition_cost) : null,
        department_id: data.department_id || null,
        description: data.description || null,
      };
      const res = await assetService.registerAsset(payload);
      toast.success(`Asset ${res.asset_tag} registered successfully!`);
      navigate(ROUTES.ASSETS);
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.detail || "Failed to register asset.");
    } finally {
      setIsSubmitting(false);
    }
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

            {/* Asset Tag Info */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Asset Tag</label>
              <input className={styles.input} value="Auto-generated upon registration" disabled readOnly />
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
                className={`${styles.select} ${errors.category_id ? styles.inputError : ""}`}
                {...register("category_id")}
              >
                <option value="">Select category…</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
              {errors.category_id && <span className={styles.errorText}>{errors.category_id.message}</span>}
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
                {CONDITIONS.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              {errors.condition && <span className={styles.errorText}>{errors.condition.message}</span>}
            </div>

            {/* Location */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Location *</label>
              <select
                className={`${styles.select} ${errors.location_id ? styles.inputError : ""}`}
                {...register("location_id")}
              >
                <option value="">Select location…</option>
                {locations.map((l) => (
                  <option key={l.id} value={l.id}>{l.name}</option>
                ))}
              </select>
              {errors.location_id && <span className={styles.errorText}>{errors.location_id.message}</span>}
            </div>

            {/* Department */}
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Owning Department</label>
              <select className={styles.select} {...register("department_id")}>
                <option value="">Select department…</option>
                {departments.map((d) => (
                  <option key={d.id} value={d.id}>{d.name}</option>
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
