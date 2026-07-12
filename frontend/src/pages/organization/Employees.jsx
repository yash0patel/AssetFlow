/**
 * pages/organization/Employees.jsx
 * ────────────────────────────────
 * Tab C of Organization Setup: Employee Directory
 */

import OrganizationTabs from "./components/OrganizationTabs";
import styles from "./organization.module.css";
import toast from "react-hot-toast";

const MOCK_EMPLOYEES = [
  { id: 1, name: "Aditi Rao", email: "aditi@company.com", department: "Engineering", role: "Department Head", status: "Active" },
  { id: 2, name: "Rohan Mehta", email: "rohan@company.com", department: "Facilities", role: "Asset Manager", status: "Active" },
  { id: 3, name: "Jane Doe", email: "jane@company.com", department: "Engineering", role: "Employee", status: "Active" },
  { id: 4, name: "Sana Iqbal", email: "sana@company.com", department: "Field Ops (East)", role: "Department Head", status: "Inactive" },
];

export default function Employees() {
  const handleAdd = () => {
    toast("Add Employee modal would open here (mock).");
  };

  return (
    <div className={styles.container}>
      <OrganizationTabs onAddClick={handleAdd} addLabel="+ Add" />

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Department</th>
              <th>Role</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_EMPLOYEES.map((emp) => (
              <tr key={emp.id}>
                <td className={styles.primaryText}>{emp.name}</td>
                <td>{emp.email}</td>
                <td>{emp.department}</td>
                <td>
                  {/* Highlight special roles for clarity */}
                  <span style={{ fontWeight: emp.role !== 'Employee' ? 600 : 400 }}>
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className={styles.footerHint}>
        Admin promotes an Employee to Department Head or Asset Manager here — this is the only place roles are assigned.
      </div>
    </div>
  );
}
