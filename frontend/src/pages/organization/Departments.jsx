/**
 * pages/organization/Departments.jsx
 * ──────────────────────────────────
 * Tab A of Organization Setup: Department Management
 */

import OrganizationTabs from "./components/OrganizationTabs";
import styles from "./organization.module.css";
import toast from "react-hot-toast";

const MOCK_DEPARTMENTS = [
  { id: 1, name: "Engineering", head: "aditi rao", parent: "--", status: "Active" },
  { id: 2, name: "Facilities", head: "rohan mehta", parent: "--", status: "Active" },
  { id: 3, name: "Field ops (east)", head: "sana iqbal", parent: "Field Ops", status: "Inactive" },
];

export default function Departments() {
  const handleAdd = () => {
    toast("Add Department modal would open here (mock).");
  };

  return (
    <div className={styles.container}>
      <OrganizationTabs onAddClick={handleAdd} addLabel="+ Add" />

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Department</th>
              <th>Head</th>
              <th>Parent Dept</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_DEPARTMENTS.map((dept) => (
              <tr key={dept.id}>
                <td className={styles.primaryText}>{dept.name}</td>
                <td>{dept.head}</td>
                <td>{dept.parent}</td>
                <td>
                  <span
                    className={`${styles.statusBadge} ${
                      dept.status === "Active" ? styles.statusActive : styles.statusInactive
                    }`}
                  >
                    {dept.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className={styles.footerHint}>
        Editing a department here also drives the picklist in Screen 4 & 5
      </div>
    </div>
  );
}
