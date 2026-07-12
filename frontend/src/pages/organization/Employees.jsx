/**
 * pages/organization/Employees.jsx
 * ────────────────────────────────
 * Tab C of Organization Setup: Employee Directory
 */

import { useState, useEffect, useCallback } from "react";
import OrganizationTabs from "./components/OrganizationTabs";
import styles from "./organization.module.css";
import toast from "react-hot-toast";
import employeeService from "../../services/employee.service";
import departmentService from "../../services/department.service";
import { useAuth } from "@hooks/useAuth";

export default function Employees() {
  const { user: currentUser } = useAuth();
  const isAdmin = currentUser?.role === "admin";

  // Data list state
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [pages, setPages] = useState(0);

  // Filters & Controls state
  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState("asc");

  // Dropdown lists
  const [departmentsList, setDepartmentsList] = useState([]);
  const [managersList, setManagersList] = useState([]);
  const [unlinkedUsers, setUnlinkedUsers] = useState([]);

  // Modals state
  const [showAddEditModal, setShowAddEditModal] = useState(false);
  const [editingEmp, setEditingEmp] = useState(null);
  const [addEditFormData, setAddEditFormData] = useState({
    user_id: "",
    department_id: "",
    designation: "",
    reporting_manager_id: "",
    date_of_joining: "",
    status: "Active",
  });

  const [showPromoteModal, setShowPromoteModal] = useState(false);
  const [promotingEmp, setPromotingEmp] = useState(null);
  const [promoteRole, setPromoteRole] = useState("Department Head");

  // Fetch employees list
  const fetchEmployees = useCallback(async () => {
    try {
      const params = {
        search: search || undefined,
        department_id: deptFilter || undefined,
        status: statusFilter || undefined,
        page,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      const data = await employeeService.listEmployees(params);
      setEmployees(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to load employees.");
    }
  }, [search, deptFilter, statusFilter, page, pageSize, sortBy, sortOrder]);

  // Load static/reference data for modals and dropdowns
  const loadReferenceData = useCallback(async (empId = null) => {
    try {
      // 1. Fetch active departments list
      const resDepts = await departmentService.listDepartments({ status: "Active", page_size: 100 });
      setDepartmentsList(resDepts.items);

      // 2. Fetch other active employees for manager dropdown selection
      const resEmps = await employeeService.listEmployees({ status: "Active", page_size: 100 });
      const filteredEmps = resEmps.items.filter((e) => e.id !== empId);
      setManagersList(filteredEmps);

      // 3. Fetch users who don't have an employee record yet (only needed when adding new)
      if (!empId) {
        const resUsers = await employeeService.listUsersWithoutEmployee();
        setUnlinkedUsers(resUsers);
      }
    } catch (err) {
      console.error("Failed to load reference lists", err);
    }
  }, []);

  useEffect(() => {
    fetchEmployees();
  }, [fetchEmployees]);

  // Load department list for top filter dropdown on mount
  useEffect(() => {
    departmentService
      .listDepartments({ status: "Active", page_size: 100 })
      .then((data) => setDepartmentsList(data.items))
      .catch((e) => console.error("Error loading filter depts", e));
  }, []);

  const handleSearchChange = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  const handleDeptFilterChange = (e) => {
    setDeptFilter(e.target.value);
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

  // Open add modal
  const handleAddClick = () => {
    if (!isAdmin) {
      toast.error("Access denied. Admin role required.");
      return;
    }
    setEditingEmp(null);
    setAddEditFormData({
      user_id: "",
      department_id: "",
      designation: "",
      reporting_manager_id: "",
      date_of_joining: "",
      status: "Active",
    });
    loadReferenceData(null);
    setShowAddEditModal(true);
  };

  // Open edit modal
  const handleEditClick = (emp) => {
    if (!isAdmin) {
      toast.error("Access denied. Admin role required.");
      return;
    }
    setEditingEmp(emp);
    setAddEditFormData({
      user_id: emp.user_id,
      department_id: emp.department_id || "",
      designation: emp.designation || "",
      reporting_manager_id: emp.reporting_manager_id || "",
      date_of_joining: emp.date_of_joining || "",
      status: emp.status,
    });
    loadReferenceData(emp.id);
    setShowAddEditModal(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAddEditFormData((prev) => ({ ...prev, [name]: value }));
  };

  // Submit create or update employee
  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!editingEmp && !addEditFormData.user_id) {
      toast.error("Linking a user account is required.");
      return;
    }

    try {
      const payload = {
        department_id: addEditFormData.department_id || null,
        designation: addEditFormData.designation.trim() || null,
        reporting_manager_id: addEditFormData.reporting_manager_id || null,
        date_of_joining: addEditFormData.date_of_joining || null,
        status: addEditFormData.status,
      };

      if (editingEmp) {
        await employeeService.updateEmployee(editingEmp.id, payload);
        toast.success("Employee record updated successfully.");
      } else {
        payload.user_id = addEditFormData.user_id;
        await employeeService.createEmployee(payload);
        toast.success("Employee record created successfully.");
      }
      setShowAddEditModal(false);
      fetchEmployees();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save employee.");
    }
  };

  // Open role assignment modal
  const handlePromoteClick = (emp) => {
    if (!isAdmin) {
      toast.error("Access denied. Admin role required.");
      return;
    }
    if (emp.status === "Inactive") {
      toast.error("Cannot change role of an inactive employee.");
      return;
    }
    setPromotingEmp(emp);
    setPromoteRole(emp.role || "Employee");
    setShowPromoteModal(true);
  };

  // Submit role update
  const handlePromoteSubmit = async (e) => {
    e.preventDefault();
    if (!promotingEmp) return;

    try {
      const payload = {
        role: promoteRole,
        department_scope_id: promoteRole === "Department Head" ? promotingEmp.department_id : null,
      };

      if (promoteRole === "Department Head" && !promotingEmp.department_id) {
        toast.error("Employee must belong to a department to be promoted to Department Head.");
        return;
      }

      await employeeService.promoteEmployee(promotingEmp.id, payload);
      toast.success(`Role updated successfully for ${promotingEmp.name}.`);
      setShowPromoteModal(false);
      fetchEmployees();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to update role.");
    }
  };

  return (
    <div className={styles.container}>
      <OrganizationTabs onAddClick={handleAddClick} addLabel="+ Add" />

      {/* Filters and Controls */}
      <div className={styles.controlsRow}>
        <input
          type="text"
          placeholder="Search by name, email, code..."
          value={search}
          onChange={handleSearchChange}
          className={styles.searchInput}
        />
        <select
          value={deptFilter}
          onChange={handleDeptFilterChange}
          className={styles.filterSelect}
        >
          <option value="">All Departments</option>
          {departmentsList.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
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
                Name {sortBy === "name" && (sortOrder === "asc" ? "▲" : "▼")}
              </th>
              <th onClick={() => toggleSort("employee_code")} style={{ cursor: "pointer" }}>
                Code {sortBy === "employee_code" && (sortOrder === "asc" ? "▲" : "▼")}
              </th>
              <th>Email</th>
              <th>Department</th>
              <th>Designation</th>
              <th>Manager</th>
              <th>Role</th>
              <th>Status</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {employees.length === 0 ? (
              <tr>
                <td colSpan={isAdmin ? 9 : 8} style={{ textAlign: "center" }}>
                  No employees found.
                </td>
              </tr>
            ) : (
              employees.map((emp) => {
                const isSelf = currentUser?.id === emp.user_id;
                return (
                  <tr key={emp.id}>
                    <td className={styles.primaryText}>{emp.name}</td>
                    <td>{emp.employee_code}</td>
                    <td>{emp.email}</td>
                    <td>{emp.department_name || "--"}</td>
                    <td>{emp.designation || "--"}</td>
                    <td>{emp.reporting_manager_name || "--"}</td>
                    <td>
                      <span style={{ fontWeight: emp.role !== "Employee" ? 600 : 400 }}>
                        {emp.role}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`${styles.statusBadge} ${
                          emp.status === "Active" ? styles.statusActive : styles.statusInactive
                        }`}
                      >
                        {emp.status}
                      </span>
                    </td>
                    {isAdmin && (
                      <td>
                        <button
                          onClick={() => handleEditClick(emp)}
                          className={`${styles.actionBtn} ${styles.actionEdit}`}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handlePromoteClick(emp)}
                          disabled={isSelf}
                          className={`${styles.actionBtn} ${styles.actionPromote}`}
                          title={isSelf ? "Self role assignment is forbidden" : ""}
                        >
                          Change Role
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pages > 1 && (
        <div className={styles.paginationRow}>
          <span className={styles.paginationText}>
            Showing page {page} of {pages} ({total} total employees)
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
      {showAddEditModal && (
        <div className={styles.modalBackdrop}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>
                {editingEmp ? "Edit Employee Information" : "Create Employee Record"}
              </h3>
              <button className={styles.closeBtn} onClick={() => setShowAddEditModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handleFormSubmit}>
              <div className={styles.modalBody}>
                {/* User selection (only for creation) */}
                {!editingEmp && (
                  <div className={styles.formGroup}>
                    <label className={styles.formLabel}>Select Registered User Account*</label>
                    <select
                      name="user_id"
                      value={addEditFormData.user_id}
                      onChange={handleInputChange}
                      className={styles.formSelect}
                      required
                    >
                      <option value="">-- Choose User --</option>
                      {unlinkedUsers.map((u) => (
                        <option key={u.id} value={u.id}>
                          {u.name} ({u.email})
                        </option>
                      ))}
                    </select>
                    {unlinkedUsers.length === 0 && (
                      <span className={styles.textSubtle} style={{ fontSize: "0.8rem", mt: 1 }}>
                        All registered users already have employee records.
                      </span>
                    )}
                  </div>
                )}

                {/* Department */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Department</label>
                  <select
                    name="department_id"
                    value={addEditFormData.department_id}
                    onChange={handleInputChange}
                    className={styles.formSelect}
                  >
                    <option value="">None / Unassigned</option>
                    {departmentsList.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Designation */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Designation</label>
                  <input
                    type="text"
                    name="designation"
                    value={addEditFormData.designation}
                    onChange={handleInputChange}
                    className={styles.formInput}
                    placeholder="e.g. Senior Software Engineer"
                  />
                </div>

                {/* Reporting Manager */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Reporting Manager</label>
                  <select
                    name="reporting_manager_id"
                    value={addEditFormData.reporting_manager_id}
                    onChange={handleInputChange}
                    className={styles.formSelect}
                  >
                    <option value="">None / Direct Report</option>
                    {managersList.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.name} ({m.employee_code})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Date of Joining */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Date of Joining</label>
                  <input
                    type="date"
                    name="date_of_joining"
                    value={addEditFormData.date_of_joining}
                    onChange={handleInputChange}
                    className={styles.formInput}
                  />
                </div>

                {/* Status */}
                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Status</label>
                  <select
                    name="status"
                    value={addEditFormData.status}
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
                  onClick={() => setShowAddEditModal(false)}
                  className={`${styles.btn} ${styles.btnSecondary}`}
                >
                  Cancel
                </button>
                <button type="submit" className={`${styles.btn} ${styles.btnPrimary}`}>
                  {editingEmp ? "Save Changes" : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Promote Modal */}
      {/* Role Assignment Modal */}
      {showPromoteModal && promotingEmp && (
        <div className={styles.modalBackdrop}>
          <div className={styles.modalContent}>
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>Change Role: {promotingEmp.name}</h3>
              <button className={styles.closeBtn} onClick={() => setShowPromoteModal(false)}>
                &times;
              </button>
            </div>
            <form onSubmit={handlePromoteSubmit}>
              <div className={styles.modalBody}>
                <p>
                  Assign a new role to this user. Select the target role below.
                </p>

                <div className={styles.formGroup}>
                  <label className={styles.formLabel}>Target Role*</label>
                  <select
                    value={promoteRole}
                    onChange={(e) => setTranslateRole(e.target.value)}
                    className={styles.formSelect}
                    required
                  >
                    <option value="Admin">Admin</option>
                    <option value="Asset Manager">Asset Manager</option>
                    <option value="Department Head">Department Head</option>
                    <option value="Employee">Employee</option>
                  </select>
                </div>

                {promoteRole === "Department Head" && (
                  <div style={{ marginTop: "10px", fontSize: "0.875rem" }}>
                    <strong>Note:</strong> Assigning Department Head will automatically assign
                    this employee as the head of their department (
                    {promotingEmp.department_name || "None - please assign department first"}).
                  </div>
                )}

                {promoteRole === "Employee" && (
                  <div style={{ marginTop: "10px", fontSize: "0.875rem" }}>
                    <strong>Note:</strong> Resetting to standard Employee will revoke all special management/admin privileges.
                  </div>
                )}
              </div>
              <div className={styles.modalFooter}>
                <button
                  type="button"
                  onClick={() => setShowPromoteModal(false)}
                  className={`${styles.btn} ${styles.btnSecondary}`}
                >
                  Cancel
                </button>
                <button type="submit" className={`${styles.btn} ${styles.btnPrimary}`}>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className={styles.footerHint}>
        Admin manages employee role assignments here — assigning Admin, Asset Manager, Department Head, or Employee roles directly.
      </div>
    </div>
  );

  // Quick helper to handle React select set state cleanly
  function setTranslateRole(val) {
    setPromoteRole(val);
  }
}
