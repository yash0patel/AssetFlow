/**
 * routes/AppRoutes.jsx
 * ─────────────────────
 * Central route configuration for the entire application.
 * Uses React Router v6 data-router (createBrowserRouter) API with lazy loading.
 */

import { lazy, Suspense } from "react";
import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";

import PrivateRoute from "./PrivateRoute";
import RoleRoute from "./RoleRoute";
import { ROUTES } from "./routeConstants";

// ── Lazy-loaded pages ──────────────────────────────────────────────────────────
// Auth
const Login = lazy(() => import("@pages/auth/Login"));
const Register = lazy(() => import("@pages/auth/Register"));
const ForgotPassword = lazy(() => import("@pages/auth/ForgotPassword"));

// Dashboard
const Dashboard = lazy(() => import("@pages/dashboard/Dashboard"));

// Organization
const Departments = lazy(() => import("@pages/organization/Departments"));
const Employees = lazy(() => import("@pages/organization/Employees"));
const AssetCategories = lazy(() => import("@pages/organization/AssetCategories"));

// Assets
const AssetList = lazy(() => import("@pages/assets/AssetList"));
const AssetDetails = lazy(() => import("@pages/assets/AssetDetails"));
const RegisterAsset = lazy(() => import("@pages/assets/RegisterAsset"));

// Feature pages
const Allocations = lazy(() => import("@pages/allocation/Allocations"));
const Bookings = lazy(() => import("@pages/bookings/Bookings"));
const Maintenance = lazy(() => import("@pages/maintenance/Maintenance"));
const Audits = lazy(() => import("@pages/audits/Audits"));
const Reports = lazy(() => import("@pages/reports/Reports"));
const Notifications = lazy(() => import("@pages/notifications/Notifications"));
const ActivityLogs = lazy(() => import("@pages/activitylogs/ActivityLogs"));
const Profile = lazy(() => import("@pages/profile/Profile"));

// ── Layouts ────────────────────────────────────────────────────────────────────
const MainLayout = lazy(() => import("@layouts/MainLayout"));
const AuthLayout = lazy(() => import("@layouts/AuthLayout"));

// ── Loading fallback ───────────────────────────────────────────────────────────
const PageLoader = () => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
    Loading…
  </div>
);

// ── Router definition ──────────────────────────────────────────────────────────
const router = createBrowserRouter([
  // Public routes (wrapped in AuthLayout)
  {
    element: (
      <Suspense fallback={<PageLoader />}>
        <AuthLayout />
      </Suspense>
    ),
    children: [
      { path: ROUTES.LOGIN, element: <Login /> },
      { path: ROUTES.REGISTER, element: <Register /> },
      { path: ROUTES.FORGOT_PASSWORD, element: <ForgotPassword /> },
    ],
  },

  // Protected routes (wrapped in MainLayout + PrivateRoute)
  {
    element: (
      <Suspense fallback={<PageLoader />}>
        <PrivateRoute />
      </Suspense>
    ),
    children: [
      {
        element: <MainLayout />,
        children: [
          { index: true, element: <Navigate to={ROUTES.DASHBOARD} replace /> },
          { path: ROUTES.DASHBOARD, element: <Dashboard /> },

          // Organization — admin/manager only
          {
            element: <RoleRoute allowedRoles={["admin", "super_admin", "manager"]} />,
            children: [
              { path: ROUTES.DEPARTMENTS, element: <Departments /> },
              { path: ROUTES.EMPLOYEES, element: <Employees /> },
              { path: ROUTES.ASSET_CATEGORIES, element: <AssetCategories /> },
            ],
          },

          // Assets
          { path: ROUTES.ASSETS, element: <AssetList /> },
          { path: ROUTES.ASSET_DETAILS, element: <AssetDetails /> },
          { path: ROUTES.ASSET_REGISTER, element: <RegisterAsset /> },

          // Features
          { path: ROUTES.ALLOCATIONS, element: <Allocations /> },
          { path: ROUTES.BOOKINGS, element: <Bookings /> },
          { path: ROUTES.MAINTENANCE, element: <Maintenance /> },
          { path: ROUTES.AUDITS, element: <Audits /> },
          { path: ROUTES.REPORTS, element: <Reports /> },
          { path: ROUTES.NOTIFICATIONS, element: <Notifications /> },
          { path: ROUTES.ACTIVITY_LOGS, element: <ActivityLogs /> },
          { path: ROUTES.PROFILE, element: <Profile /> },
        ],
      },
    ],
  },

  // Catch-all → login
  { path: "*", element: <Navigate to={ROUTES.LOGIN} replace /> },
]);

export default function AppRoutes() {
  return <RouterProvider router={router} />;
}
