/**
 * pages/organization/AssetCategories.jsx
 * ──────────────────────────────────────
 * Tab B of Organization Setup: Asset Category Management
 */

import { useState, useEffect, useCallback } from "react";
import OrganizationTabs from "./components/OrganizationTabs";
import styles from "./organization.module.css";
import toast from "react-hot-toast";
import assetCategoryService from "../../services/asset-category.service";
import { useAuth } from "@hooks/useAuth";

export default function AssetCategories() {
  const { user } = useAuth();
  const isAdmin = user?.role === "Admin";

  // Listing state
  const [categories, setCategories] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [pages, setPages] = useState(0);

  // Search & Filter state
  const [search, setSearch] = useState("");
  const [isActiveFilter, setIsActiveFilter] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  // Modal form state
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    parent_category_id: "",
    description: "",
    default_useful_life_months: "",
    is_active: true,
    attributes: [],
  });

  // Category dropdown for parent category select
  const [parentCategories, setParentCategories] = useState([]);

  // Fetch categories data
  const fetchCategories = useCallback(async () => {
    try {
      const params = {
        search: search || undefined,
        is_active: isActiveFilter === "" ? undefined : isActiveFilter === "true",
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      const data = await assetCategoryService.listCategories(params);
      setCategories(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to load categories.");
    }
  }, [search, isActiveFilter, page, pageSize, sortBy, sortOrder]);

  // Load parent categories dropdown
  const loadParentCategories = useCallback(async (catId = null) => {
    try {
      const res = await assetCategoryService.listCategories({ is_active: true, page_size: 100 });
      // Filter out self to avoid parent-child loop
      const filtered = res.items.filter((c) => c.id !== catId);
      setParentCategories(filtered);
    } catch (err) {
      console.error("Failed to load parent categories", err);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  const handleFilterChange = (e) => {
    setIsActiveFilter(e.target.value);
    setPage(1);
  };

  const toggleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
    setPage(1);
  };

  // Open modal for add
  const handleAddClick = () => {
    if (!isAdmin) {
      toast.error("Access denied. Admin role required.");
      return;
    }
    setEditingCategory(null);
    setFormData({
      name: "",
      parent_category_id: "",
      description: "",
      default_useful_life_months: "",
      is_active: true,
      attributes: [],
    });
    loadParentCategories(null);
    setShowModal(true);
  };

  // Open modal for edit
  const handleEditClick = (cat) => {
    if (!isAdmin) {
      toast.error("Access denied. Admin role required.");
      return;
    }
    setEditingCategory(cat);
    setFormData({
      name: cat.name,
      parent_category_id: cat.parent_category_id || "",
      description: cat.description || "",
      default_useful_life_months: cat.default_useful_life_months || "",
      is_active: cat.is_active,
      attributes: cat.attributes || [],
    });
    loadParentCategories(cat.id);
    setShowModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  // Attribute list helpers
  const handleAddAttribute = () => {
    setFormData((prev) => ({
      ...prev,
      attributes: [
        ...prev.attributes,
        {
          attribute_key: "",
          attribute_label: "",
          data_type: "TEXT",
          select_options: "",
          is_required: false,
          display_order: prev.attributes.length,
        },
      ],
    }));
  };

  const handleAttributeChange = (index, field, value) => {
    setFormData((prev) => {
      const updated = [...prev.attributes];
      updated[index] = { ...updated[index], [field]: value };
      
      // Automatically derive attribute_key from label if label is modified
      if (field === "attribute_label") {
        updated[index].attribute_key = value
          .toLowerCase()
          .replace(/[^a-z0-9_]+/g, "_")
          .replace(/(^_|_$)/g, "");
      }
      
      return { ...prev, attributes: updated };
    });
  };

  const handleRemoveAttribute = (index) => {
    setFormData((prev) => ({
      ...prev,
      attributes: prev.attributes.filter((_, i) => i !== index),
    }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error("Category name is required.");
      return;
    }

    // Format attributes before payload submission
    const formattedAttributes = formData.attributes.map((attr, idx) => {
      let options = null;
      if (attr.data_type === "SELECT" && typeof attr.select_options === "string") {
        options = {
          choices: attr.select_options
            .split(",")
            .map((o) => o.trim())
            .filter((o) => o !== ""),
        };
      } else if (attr.data_type === "SELECT") {
        options = attr.select_options;
      }
      return {
        attribute_key: attr.attribute_key || attr.attribute_label.toLowerCase().replace(/\s+/g, "_"),
        attribute_label: attr.attribute_label,
        data_type: attr.data_type,
        select_options: options,
        is_required: attr.is_required,
        display_order: idx,
      };
    });

    // Validate attributes have label
    for (const attr of formattedAttributes) {
      if (!attr.attribute_label.trim()) {
        toast.error("All custom attributes must have a label.");
        return;
      }
    }

    try {
      const payload = {
        name: formData.name.trim(),
        parent_category_id: formData.parent_category_id || null,
        description: formData.description.trim() || null,
        default_useful_life_months: formData.default_useful_life_months
          ? parseInt(formData.default_useful_life_months)
          : null,
        is_active: formData.is_active,
        attributes: formattedAttributes,
      };

      if (editingCategory) {
        await assetCategoryService.updateCategory(editingCategory.id, payload);
        toast.success("Category updated successfully.");
      } else {
        await assetCategoryService.createCategory(payload);
        toast.success("Category created successfully.");
      }
      setShowModal(false);
      fetchCategories();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save category.");
    }
  };

  const handleDeleteClick = async (cat) => {
    if (!isAdmin) {
      toast.error("Access denied. Admin role required.");
      return;
    }
    if (window.confirm(`Are you sure you want to delete category ${cat.name}?`)) {
      try {
        await assetCategoryService.deleteCategory(cat.id);
        toast.success("Category deleted successfully.");
        fetchCategories();
      } catch (err) {
        toast.error(err.response?.data?.detail || "Failed to delete category.");
      }
    }
  };

  return (
    <div className={styles.container}>
      <OrganizationTabs onAddClick={handleAddClick} addLabel="+ Add" />

      {/* Controls */}
      <div className={styles.controlsRow}>
        <input
          type="text"
          placeholder="Search by category name..."
          value={search}
          onChange={handleSearchChange}
          className={styles.searchInput}
        />
        <select
          value={isActiveFilter}
          onChange={handleFilterChange}
          className={styles.filterSelect}
        >
          <option value="">All Statuses</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th onClick={() => toggleSort("name")} style={{ cursor: "pointer" }}>
                Category Name {sortBy === "name" && (sortOrder === "asc" ? "▲" : "▼")}
              </th>
              <th>Description</th>
              <th>Parent Category</th>
              <th>Useful Life (Months)</th>
              <th>Status</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {categories.length === 0 ? (
              <tr>
                <td colSpan={isAdmin ? 6 : 5} style={{ textAlign: "center" }}>
                  No categories found.
                </td>
              </tr>
            ) : (
              categories.map((cat) => (
                <tr key={cat.id}>
                  <td className={styles.primaryText}>{cat.name}</td>
                  <td>{cat.description || "--"}</td>
                  <td>{cat.parent_name || "--"}</td>
                  <td>{cat.default_useful_life_months || "--"}</td>
                  <td>
                    <span
                      className={`${styles.statusBadge} ${
                        cat.is_active ? styles.statusActive : styles.statusInactive
                      }`}
                    >
                      {cat.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  {isAdmin && (
                    <td>
                      <button
                        onClick={() => handleEditClick(cat)}
                        className={`${styles.actionBtn} ${styles.actionEdit}`}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteClick(cat)}
                        className={`${styles.actionBtn} ${styles.actionDelete}`}
                      >
                        Delete
                      </button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pages > 1 && (
        <div className={styles.paginationRow}>
          <span className={styles.paginationText}>
            Showing page {page} of {pages} ({total} total categories)
          </span>
          <div className={styles.paginationBtns}>
            <button
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page === 1}
              className={styles.paginationBtn}
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => Math.min(p + 1, pages))}
              disabled={page === pages}
              className={styles.paginationBtn}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Add / Edit Modal */}
      {showModal && (
        <div className={styles.modalBackdrop}>
          <div className={styles.modalContent} style={{ maxWidth: "600px" }}>
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>
                {editingCategory ? "Edit Category" : "Add Category"}
              </h3>
              <button className={styles.closeBtn} onClick={() => setShowModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleFormSubmit}>
              <div className={styles.modalBody} style={{ maxHeight: "60vh" }}>
                {/* Name */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Category Name*</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className={styles.formInput}
                    placeholder="e.g. Laptops"
                    required
                  />
                </div>

                {/* Parent category */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Parent Category</label>
                  <select
                    name="parent_category_id"
                    value={formData.parent_category_id}
                    onChange={handleInputChange}
                    className={styles.formSelect}
                  >
                    <option value="">None</option>
                    {parentCategories.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Description */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Description</label>
                  <input
                    type="text"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    className={styles.formInput}
                    placeholder="Brief details about the category"
                  />
                </div>

                {/* Useful Life */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Useful Life (Months)</label>
                  <input
                    type="number"
                    name="default_useful_life_months"
                    value={formData.default_useful_life_months}
                    onChange={handleInputChange}
                    className={styles.formInput}
                    placeholder="e.g. 36"
                    min="1"
                  />
                </div>

                {/* Active check */}
                <div className={styles.formGroup} style={{ flexDirection: "row", alignItems: "center", gap: "10px" }}>
                  <input
                    type="checkbox"
                    name="is_active"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    style={{ width: "auto" }}
                  />
                  <label htmlFor="is_active" className={styles.formLabel}>
                    Active
                  </label>
                </div>

                {/* Attributes (EAV side attributes) */}
                <div style={{ marginTop: "1rem", borderTop: "1px solid var(--color-border)", paddingTop: "1rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                    <h4 style={{ fontSize: "1rem" }}>Custom Attributes</h4>
                    <button
                      type="button"
                      onClick={handleAddAttribute}
                      className={`${styles.btn} ${styles.btnSecondary}`}
                      style={{ padding: "4px 10px", fontSize: "0.8rem" }}
                    >
                      + Add Attribute
                    </button>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {formData.attributes.map((attr, index) => (
                      <div
                        key={index}
                        style={{
                          display: "grid",
                          gridTemplateColumns: "2fr 1.5fr 1fr 40px",
                          gap: "8px",
                          alignItems: "center",
                          backgroundColor: "var(--color-surface-2)",
                          padding: "8px",
                          borderRadius: "var(--radius-md)",
                        }}
                      >
                        <div>
                          <input
                            type="text"
                            placeholder="Label (e.g. Warranty)"
                            value={attr.attribute_label}
                            onChange={(e) => handleAttributeChange(index, "attribute_label", e.target.value)}
                            className={styles.formInput}
                            style={{ padding: "4px" }}
                            required
                          />
                        </div>
                        <div>
                          <select
                            value={attr.data_type}
                            onChange={(e) => handleAttributeChange(index, "data_type", e.target.value)}
                            className={styles.formSelect}
                            style={{ padding: "4px" }}
                          >
                            <option value="TEXT">TEXT</option>
                            <option value="NUMBER">NUMBER</option>
                            <option value="DATE">DATE</option>
                            <option value="BOOLEAN">BOOLEAN</option>
                            <option value="SELECT">SELECT</option>
                          </select>
                        </div>
                        <div style={{ display: "flex", alignItems: "center", gap: "4px", justifyContent: "center" }}>
                          <input
                            type="checkbox"
                            checked={attr.is_required}
                            id={`req-${index}`}
                            onChange={(e) => handleAttributeChange(index, "is_required", e.target.checked)}
                            style={{ width: "auto" }}
                          />
                          <label htmlFor={`req-${index}`} style={{ fontSize: "0.75rem" }}>
                            Req
                          </label>
                        </div>
                        <div>
                          <button
                            type="button"
                            onClick={() => handleRemoveAttribute(index)}
                            className={`${styles.btn} ${styles.btnDanger}`}
                            style={{ padding: "4px 8px", fontSize: "0.8rem" }}
                          >
                            &times;
                          </button>
                        </div>

                        {attr.data_type === "SELECT" && (
                          <div style={{ gridColumn: "span 4" }}>
                            <input
                              type="text"
                              placeholder="Comma-separated options (e.g. 1 year, 2 years, 3 years)"
                              value={
                                typeof attr.select_options === "object" && attr.select_options !== null
                                  ? attr.select_options.choices?.join(", ") || ""
                                  : attr.select_options || ""
                              }
                              onChange={(e) => handleAttributeChange(index, "select_options", e.target.value)}
                              className={styles.formInput}
                              style={{ padding: "4px" }}
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              <div className={styles.modalFooter}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className={`${styles.btn} ${styles.btnSecondary}`}
                >
                  Cancel
                </button>
                <button type="submit" className={`${styles.btn} ${styles.btnPrimary}`}>
                  {editingCategory ? "Save Changes" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
