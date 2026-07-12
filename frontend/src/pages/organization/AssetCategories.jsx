/**
 * pages/organization/AssetCategories.jsx
 * ──────────────────────────────────────
 * Tab B of Organization Setup: Asset Category Management
 */

import OrganizationTabs from "./components/OrganizationTabs";
import styles from "./organization.module.css";
import toast from "react-hot-toast";

const MOCK_CATEGORIES = [
  { id: 1, name: "Electronics", description: "Laptops, Monitors, Phones", status: "Active" },
  { id: 2, name: "Furniture", description: "Desks, Chairs, Cabinets", status: "Active" },
  { id: 3, name: "Vehicles", description: "Company Cars, Vans", status: "Inactive" },
];

export default function AssetCategories() {
  const handleAdd = () => {
    toast("Add Category modal would open here (mock).");
  };

  return (
    <div className={styles.container}>
      <OrganizationTabs onAddClick={handleAdd} addLabel="+ Add" />

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Category Name</th>
              <th>Description</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {MOCK_CATEGORIES.map((cat) => (
              <tr key={cat.id}>
                <td className={styles.primaryText}>{cat.name}</td>
                <td>{cat.description}</td>
                <td>
                  <span
                    className={`${styles.statusBadge} ${
                      cat.status === "Active" ? styles.statusActive : styles.statusInactive
                    }`}
                  >
                    {cat.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
