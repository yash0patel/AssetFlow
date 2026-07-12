/**
 * pages/organization/Departments.jsx
 * ──────────────────────────────────
 * Tab A of Organization Setup: Department Management
 */

import { useState, useEffect, useCallback } from "react";
import OrganizationTabs from "./components/OrganizationTabs";
import styles from "./organization.module.css";
import toast from "react-hot-toast";
import departmentService from "../../services/department.service";
import employeeService from "../../services/employee.service";
import { useAuth } from "@hooks/useAuth";

export default function Departments() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  // State for data listing
  const [departments, setDepartments] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [pages, setPages] = useState(0);

  // Search & Filter state
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  // Modal form state
  const [showModal, setShowModal] = useState(false);
  const [editingDept, setEditingDept] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    parent_department_id: "",
    primary_location_id: "",
    status: "Active",
    head_employee_id: "",
  });

  // Reference lists for dropdowns
  const [activeDepts, setActiveDepts] = useState([]);
  const [eligibleHeads, setEligibleHeads] = useState([]);

  // Fetch departments data
  const fetchDepartments = useCallback(async () => {
    try {
      const params = {
        search: search || undefined,
        status: statusFilter || undefined,
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      const data = await departmentService.listDepartments(params);
      setDepartments(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to load departments.");
    }
  }, [search, statusFilter, page, pageSize, sortBy, sortOrder]);

  // Load dropdown lists
  const loadDropdownData = useCallback(async (deptId = null) => {
    try {
      // 1. Fetch active departments for parent list (limit 100 for dropdown)
      const resDepts = await departmentService.listDepartments({ status: "Active", page_size: 100 });
      // Exclude self from parent list to prevent self-parent cycles
      const filteredDepts = resDepts.items.filter((d) => d.id !== deptId);
      setActiveDepts(filteredDepts);

      // 2. Fetch active employees of this department if editing to populate head list
      if (deptId) {
        const resEmps = await employeeService.listEmployees({ department_id: deptId, status: "Active", page_size: 100 });
        setEligibleHeads(resEmps.items);
      } else {
        setEligibleHeads([]);
      }
    } catch (err) {
      console.error("Failed to load reference data", err);
    }
  }, []);

  useEffect(() => {
    fetchDepartments();
  }, [fetchDepartments]);

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
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
    setEditingDept(null);
    setFormData({
      name: "",
      code: "",
      parent_department_id: "",
      primary_location_id: "",
      status: "Active",
      head_employee_id: "",
    });
    loadDropdownData(null);
    setShowModal(true);
  };

  // Open modal for edit
  const handleEditClick = (dept) => {
    if (!isAdmin) {
      toast.error("Access denied. Admin role required.");
      return;
    }
    setEditingDept(dept);
    setFormData({
      name: dept.name,
      code: dept.code || "",
      parent_department_id: dept.parent_department_id || "",
      primary_location_id: dept.primary_location_id || "",
      status: dept.status,
      head_employee_id: dept.head_employee_id || "",
    });
    loadDropdownData(dept.id);
    setShowModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Submit add/edit form
  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error("Department name is required.");
      return;
    }

    try {
      const payload = {
        name: formData.name.trim(),
        code: formData.code.trim() || null,
        parent_department_id: formData.parent_department_id || null,
        primary_location_id: formData.primary_location_id || null,
        status: formData.status,
      };

      if (editingDept) {
        // Include head employee when updating
        payload.head_employee_id = formData.head_employee_id || null;
        await departmentService.updateDepartment(editingDept.id, payload);
        toast.success("Department updated successfully.");
      } else {
        await departmentService.createDepartment(payload);
        toast.success("Department created successfully.");
      }
      setShowModal(false);
      fetchDepartments();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save department.");
    }
  };

  // Delete/Deactivate
  const handleDeleteClick = async (dept) => {
    if (!isAdmin) {
      toast.error("Access denied. Admin role required.");
      return;
    }
    if (window.confirm(`Are you sure you want to delete department ${dept.name}?`)) {
      try {
        await departmentService.deleteDepartment(dept.id);
        toast.success("Department deleted successfully.");
        fetchDepartments();
      } catch (err) {
        toast.error(err.response?.data?.detail || "Failed to delete department.");
      }
    }
  };

  return (
    <div className={styles.container}>
      <OrganizationTabs onAddClick={handleAddClick} addLabel="+ Add" />

      {/* Search and Filters */}
      <div className={styles.controlsRow}>
        <input
          type="text"
          placeholder="Search by name or code..."
          value={search}
          onChange={handleSearchChange}
          className={styles.searchInput}
        />
        <select
          value={statusFilter}
          onChange={handleStatusFilterChange}
          className={styles.filterSelect}
        >
          <option value="">All Statuses</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
        </select>
      </div>

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th onClick={() => toggleSort("name")} style={{ cursor: "pointer" }}>
                Department {sortBy === "name" && (sortOrder === "asc" ? "▲" : "▼")}
              </th>
              <th onClick={() => toggleSort("code")} style={{ cursor: "pointer" }}>
                Code {sortBy === "code" && (sortOrder === "asc" ? "▲" : "▼")}
              </th>
              <th>Head</th>
              <th>Parent Dept</th>
              <th>Status</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {departments.length === 0 ? (
              <tr>
                <td colSpan={isAdmin ? 6 : 5} style={{ textAlign: "center", py: 8 }}>
                  No departments found.
                </td>
              </tr>
            ) : (
              departments.map((dept) => (
                <tr key={dept.id}>
                  <td className={styles.primaryText}>{dept.name}</td>
                  <td>{dept.code || "--"}</td>
                  <td>{dept.head_name || "--"}</td>
                  <td>{dept.parent_name || "--"}</td>
                  <td>
                    <span
                      className={`${styles.statusBadge} ${
                        dept.status === "Active" ? styles.statusActive : styles.statusInactive
                      }`}
                    >
                      {dept.status}
                    </span>
                  </td>
                  {isAdmin && (
                    <td>
                      <button
                        onClick={() => handleEditClick(dept)}
                        className={`${styles.actionBtn} ${styles.actionEdit}`}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteClick(dept)}
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

      {/* Pagination Controls */}
      {pages > 1 && (
        <div className={styles.paginationRow}>
          <span className={styles.paginationText}>
            Showing page {page} of {pages} ({total} total departments)
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
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>
                {editingDept ? "Edit Department" : "Add Department"}
              </h3>
              <button className={styles.closeBtn} onClick={() => setShowModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleFormSubmit}>
              <div className={styles.modalBody}>
                {/* Name */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Department Name*</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className={styles.formInput}
                    placeholder="e.g. Engineering"
                    required
                  />
                </div>

                {/* Code */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Department Code</label>
                  <input
                    type="text"
                    name="code"
                    value={formData.code}
                    onChange={handleInputChange}
                    className={styles.formInput}
                    placeholder="e.g. ENG"
                  />
                </div>

                {/* Parent Department */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Parent Department</label>
                  <select
                    name="parent_department_id"
                    value={formData.parent_department_id}
                    onChange={handleInputChange}
                    className={styles.formSelect}
                  >
                    <option value="">None</option>
                    {activeDepts.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Head Employee (only visible when editing an existing department) */}
                {editingDept && (
                  <div className={styles.formGroup}>
                    <label className={styles.formLabel}>Department Head</label>
                    <select
                      name="head_employee_id"
                      value={formData.head_employee_id}
                      onChange={handleInputChange}
                      className={styles.formSelect}
                    >
                      <option value="">None</option>
                      {eligibleHeads.map((e) => (
                        <option key={e.id} value={e.id}>
                          {e.name} ({e.employee_code})
                        </option>
                      ))}
                    </select>
                    {eligibleHeads.length === 0 && (
                      <span className={styles.textSubtle} style={{ fontSize: "0.8rem", mt: 1 }}>
                        Only active employees belonging to this department can be selected as Head.
                      </span>
                    )}
                  </div>
                )}

                {/* Status */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Status</label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleInputChange}
                    className={styles.formSelect}
                  >
                    <option value="Active">Active</option>
                    <option value="Inactive">Inactive</option>
                  </select>
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
                  {editingDept ? "Save Changes" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className={styles.footerHint}>
        Editing a department here also drives the picklist in Screen 4 & 5
      </div>
    </div>
  );
}
