/**
 * pages/assets/mockAssets.js
 * ──────────────────────────
 * Mock data aligned with the backend Asset model.
 * Fields: asset_tag, name, category, serial_number, acquisition_date,
 *         acquisition_cost, condition, current_status, location, is_bookable
 */

export const MOCK_CATEGORIES = ["Electronics", "Furniture", "Vehicles", "Equipment"];
export const MOCK_STATUSES   = ["Available", "Allocated", "Reserved", "Under Maintenance", "Lost", "Retired", "Disposed"];
export const MOCK_CONDITIONS = ["New", "Good", "Fair", "Poor", "Damaged"];
export const MOCK_DEPARTMENTS = ["Engineering", "Facilities", "Field Ops", "HR"];
export const MOCK_LOCATIONS  = ["Bengaluru HQ", "HQ Floor 2", "Warehouse", "Remote", "Chennai Office"];

export const MOCK_ASSETS = [
  {
    id: "a1",
    asset_tag: "AF-0012",
    name: "Dell Laptop",
    category: "Electronics",
    serial_number: "DL-3928471",
    acquisition_date: "2023-06-15",
    acquisition_cost: 68000,
    condition: "Good",
    current_status: "Allocated",
    location: "Bengaluru",
    department: "Engineering",
    is_bookable: false,
    description: "Dell Latitude 5540 laptop assigned to engineering team.",
    allocation_history: [
      { date: "2024-01-10", employee: "Jane Doe", status: "Active", return_date: null },
      { date: "2023-09-01", employee: "Amit Kumar", status: "Returned", return_date: "2023-12-31" },
    ],
    maintenance_history: [
      { date: "2023-11-15", issue: "Battery replacement", status: "Resolved", technician: "Ravi Tech" },
    ],
  },
  {
    id: "a2",
    asset_tag: "AF-0062",
    name: "Projector",
    category: "Electronics",
    serial_number: "PJ-0018823",
    acquisition_date: "2022-03-20",
    acquisition_cost: 45000,
    condition: "Fair",
    current_status: "Under Maintenance",
    location: "HQ Floor 2",
    department: "Facilities",
    is_bookable: true,
    description: "Epson conference room projector.",
    allocation_history: [],
    maintenance_history: [
      { date: "2026-07-10", issue: "Lamp flickering during projection", status: "In Progress", technician: "TechCare Vendor" },
    ],
  },
  {
    id: "a3",
    asset_tag: "AF-0201",
    name: "Office Chair",
    category: "Furniture",
    serial_number: null,
    acquisition_date: "2021-11-05",
    acquisition_cost: 8500,
    condition: "Good",
    current_status: "Available",
    location: "Warehouse",
    department: "Facilities",
    is_bookable: false,
    description: "Ergonomic office chair, black color.",
    allocation_history: [
      { date: "2022-04-01", employee: "Rohan Mehta", status: "Returned", return_date: "2023-10-15" },
    ],
    maintenance_history: [],
  },
  {
    id: "a4",
    asset_tag: "AF-0305",
    name: "Toyota Innova",
    category: "Vehicles",
    serial_number: "KA01MN4567",
    acquisition_date: "2020-08-01",
    acquisition_cost: 1450000,
    condition: "Good",
    current_status: "Reserved",
    location: "Bengaluru HQ",
    department: "Field Ops",
    is_bookable: true,
    description: "Company vehicle for field operations team.",
    allocation_history: [],
    maintenance_history: [],
  },
  {
    id: "a5",
    asset_tag: "AF-0090",
    name: "HP Monitor 27\"",
    category: "Electronics",
    serial_number: "HP-9827361",
    acquisition_date: "2024-02-10",
    acquisition_cost: 22000,
    condition: "New",
    current_status: "Available",
    location: "Warehouse",
    department: "Engineering",
    is_bookable: false,
    description: "HP EliteDisplay E27 Full HD monitor.",
    allocation_history: [],
    maintenance_history: [],
  },
];

/** Returns the next sequential asset tag */
export function generateAssetTag(existingAssets) {
  const max = existingAssets.reduce((acc, a) => {
    const num = parseInt(a.asset_tag.replace("AF-", ""), 10);
    return num > acc ? num : acc;
  }, 0);
  return `AF-${String(max + 1).padStart(4, "0")}`;
}
