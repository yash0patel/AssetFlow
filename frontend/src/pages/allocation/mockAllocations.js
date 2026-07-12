/**
 * pages/allocation/mockAllocations.js
 * ─────────────────────────────────────
 * Mock data for Allocation & Transfer screen.
 * Aligned with backend models:
 *   asset_allocations  → status: Active | Returned | Overdue | Lost
 *   asset_transfer_requests → status: Requested | Approved | Rejected | Completed | Cancelled
 */

import dayjs from "dayjs";

export const MOCK_EMPLOYEES = [
  { id: "e1", name: "Priya Shah",   department: "Engineering" },
  { id: "e2", name: "Raj Patel",    department: "Engineering" },
  { id: "e3", name: "Rohan Mehta",  department: "Facilities" },
  { id: "e4", name: "Jane Doe",     department: "Engineering" },
  { id: "e5", name: "Sana Iqbal",   department: "Field Ops" },
  { id: "e6", name: "Arjun Nair",   department: "HR" },
];

const today = dayjs();

export const MOCK_ALLOCATABLE_ASSETS = [
  {
    id:          "a1",
    asset_tag:   "AF-0012",
    name:        "Dell Laptop",
    category:    "Electronics",
    // Already allocated — the conflict scenario from the mockup
    current_holder: { id: "e1", name: "Priya Shah", department: "Engineering" },
    allocation_status: "Active",
    expected_return_date: today.add(15, "day").format("YYYY-MM-DD"),
  },
  {
    id:          "a3",
    asset_tag:   "AF-0201",
    name:        "Office Chair",
    category:    "Furniture",
    current_holder: null,
    allocation_status: null,
    expected_return_date: null,
  },
  {
    id:          "a4",
    asset_tag:   "AF-0305",
    name:        "Toyota Innova",
    category:    "Vehicles",
    current_holder: null,
    allocation_status: null,
    expected_return_date: null,
  },
  {
    id:          "a5",
    asset_tag:   "AF-0090",
    name:        'HP Monitor 27"',
    category:    "Electronics",
    current_holder: null,
    allocation_status: null,
    expected_return_date: null,
  },
];

export const MOCK_ACTIVE_ALLOCATIONS = [
  {
    id:          "alloc-1",
    asset_tag:   "AF-0012",
    asset_name:  "Dell Laptop",
    employee:    "Priya Shah",
    department:  "Engineering",
    allocated_on: "2026-03-12",
    expected_return: today.add(15, "day").format("YYYY-MM-DD"),
    status:      "Active",
    overdue:     false,
  },
  {
    id:          "alloc-2",
    asset_tag:   "AF-0052",
    asset_name:  "iPad Pro",
    employee:    "Sana Iqbal",
    department:  "Field Ops",
    allocated_on: "2026-01-08",
    expected_return: today.subtract(5, "day").format("YYYY-MM-DD"), // OVERDUE
    status:      "Overdue",
    overdue:     true,
  },
  {
    id:          "alloc-3",
    asset_tag:   "AF-0034",
    asset_name:  "Canon DSLR",
    employee:    "Rohan Mehta",
    department:  "Facilities",
    allocated_on: "2026-05-01",
    expected_return: null,
    status:      "Active",
    overdue:     false,
  },
];

export const MOCK_TRANSFER_REQUESTS = [
  {
    id:       "tr-1",
    asset_tag: "AF-0012",
    asset_name: "Dell Laptop",
    from:     "Priya Shah",
    to:       "Raj Patel",
    reason:   "Raj joining new project requiring high-performance laptop.",
    status:   "Requested",
    requested_on: "2026-07-10",
  },
  {
    id:       "tr-2",
    asset_tag: "AF-0062",
    asset_name: "Projector",
    from:     "Rohan Mehta",
    to:       "Jane Doe",
    reason:   "Conference room reassignment.",
    status:   "Approved",
    requested_on: "2026-07-05",
  },
];

export const MOCK_HISTORY = [
  { date: "Mar 12", event: "Allocated to Priya Shah – Engineering" },
  { date: "Jan 04", event: "Returned by Arjun Nair – condition: Good" },
  { date: "Sep 01", event: "Allocated to Arjun Nair – HR" },
];
