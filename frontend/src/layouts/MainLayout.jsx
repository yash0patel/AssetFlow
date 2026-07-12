/**
 * layouts/MainLayout.jsx
 * ──────────────────────
 * Shell for authenticated app: Sidebar + Content
 */
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import styles from "./main-layout.module.css";

export default function MainLayout() {
  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.main}>
        {/* We can add a Header here later if needed */}
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
