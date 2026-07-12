/**
 * App.jsx
 * ────────
 * Root component. Wraps the app with all Context Providers and
 * TanStack Query client, then renders the route tree.
 */

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Toaster } from "react-hot-toast";

import { AuthProvider } from "@context/AuthContext";
import { ThemeProvider } from "@context/ThemeContext";
import { NotificationProvider } from "@context/NotificationContext";
import AppRoutes from "@routes/AppRoutes";

// ── TanStack Query client ──────────────────────────────────────────────────────
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,     // 5 minutes
      gcTime: 1000 * 60 * 10,       // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <AuthProvider>
          <NotificationProvider>
            {/* Global toast container */}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  fontFamily: "var(--font-sans)",
                  fontSize: "0.875rem",
                },
              }}
            />

            {/* Router tree */}
            <AppRoutes />

            {/* Dev tools — removed in production build */}
            {import.meta.env.VITE_ENABLE_DEVTOOLS === "true" && (
              <ReactQueryDevtools initialIsOpen={false} />
            )}
          </NotificationProvider>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
