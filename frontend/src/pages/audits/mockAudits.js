/**
 * pages/audits/mockAudits.js
 * ───────────────────────────
 * Mock data for the Asset Audit screen.
 */

export const MOCK_ACTIVE_AUDIT = {
  id: "aud1",
  title: "Q3 audit: Engineering dept",
  date_range: "1-15 jul",
  auditors: "A. Rao, S. Iqbal",
  assets: [
    {
      id: "a1",
      tag: "AF-003",
      name: "Dell laptop",
      location: "Desk E12",
      verification: "Verified",
    },
    {
      id: "a2",
      tag: "AF-9921",
      name: "Office chair",
      location: "Desk E14",
      verification: "Missing",
    },
    {
      id: "a3",
      tag: "AF-9838",
      name: "Monitor",
      location: "Desk E15",
      verification: "Damaged",
    },
    {
      id: "a4",
      tag: "AF-8821",
      name: "Keyboard",
      location: "Desk E15",
      verification: null, // Not yet verified
    }
  ]
};
