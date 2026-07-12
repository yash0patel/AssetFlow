/** layouts/MainLayout.jsx — Shell for authenticated app: Sidebar + Header + Content */
import { Outlet } from "react-router-dom";

export default function MainLayout() {
  return (
    <div className="main-layout">
      {/* Sidebar goes here */}
      {/* Header goes here */}
      <main className="main-content">
        <Outlet />
      </main>
      {/* Footer goes here */}
    </div>
  );
}
