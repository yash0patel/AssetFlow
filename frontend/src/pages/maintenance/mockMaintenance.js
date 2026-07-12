/**
 * pages/maintenance/mockMaintenance.js
 * ────────────────────────────────────
 * Mock data for the Maintenance Kanban Board.
 */

export const MOCK_MAINTENANCE_TICKETS = [
  {
    id: "m1",
    asset_tag: "AF-0062",
    asset_name: "Projector",
    issue: "Projector bulb not turning on",
    status: "Pending",
    priority: "High",
    technician: null,
    resolution_note: null,
  },
  {
    id: "m2",
    asset_tag: "AF-003",
    asset_name: "AC Unit",
    issue: "noisy compressor",
    status: "Approved",
    priority: "Medium",
    technician: null,
    resolution_note: null,
  },
  {
    id: "m3",
    asset_tag: "AF-0078",
    asset_name: "Forklift",
    issue: "Battery draining fast",
    status: "Technician assigned",
    priority: "High",
    technician: "R varma",
    resolution_note: null,
  },
  {
    id: "m4",
    asset_tag: "AF-897",
    asset_name: "Printer",
    issue: "Printer Jam parts ordered",
    status: "in progress",
    priority: "Low",
    technician: "S Gupta",
    resolution_note: null,
  },
  {
    id: "m5",
    asset_tag: "AF-873",
    asset_name: "Office Chair",
    issue: "Chair repair",
    status: "Resolved",
    priority: "Low",
    technician: "R Varma",
    resolution_note: "resolved 7 Jul",
  },
];

export const MOCK_ASSETS_LIST = [
  { id: "a1", tag: "AF-0062", name: "Projector" },
  { id: "a2", tag: "AF-003",  name: "AC Unit" },
  { id: "a3", tag: "AF-0078", name: "Forklift" },
  { id: "a4", tag: "AF-897",  name: "Printer" },
  { id: "a5", tag: "AF-873",  name: "Office Chair" },
  { id: "a6", tag: "AF-0012", name: "Dell Laptop" },
];
