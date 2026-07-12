/**
 * main.jsx
 * ─────────
 * Application entry point.
 * Mounts the React app into the #root DOM element.
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./index.css";
import App from "./App";

const rootEl = document.getElementById("root");

if (!rootEl) {
  throw new Error("Root element #root not found. Check public/index.html.");
}

createRoot(rootEl).render(
  <StrictMode>
    <App />
  </StrictMode>
);
