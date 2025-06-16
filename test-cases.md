# ✅ Test Cases for EcoTown Health Dashboard

This document outlines test scenarios to validate the functionality, reliability, and usability of the EcoTown Health Dashboard application.

---

## 📁 Section 1: File Upload

| Test ID | Test Description | Expected Outcome |
|--------|------------------|------------------|
| TC001  | Upload a valid PDF report | Charts are generated and data is displayed accurately |
| TC002  | Upload a non-PDF file (e.g., `.jpg`, `.docx`) | Error message shown: "Unsupported file format" |
| TC003  | Upload a PDF with missing biomarker values | Partial data displayed with missing values indicated |
| TC004  | Upload a blank PDF | Error message shown: "No clinical data found" |

---

## 📁 Section 2: Dashboard Rendering

| Test ID | Test Description | Expected Outcome |
|--------|------------------|------------------|
| TC005  | Render dashboard for normal biomarker values | All values shown within normal range (green indicators) |
| TC006  | Render dashboard for abnormal values | Out-of-range values highlighted in red or warning styles |
| TC007  | Check for chart rendering on different screen sizes | Charts resize and remain readable on mobile, tablet, desktop |
| TC008  | Verify that legends, axis, and tooltips appear correctly on charts | All components are visible and functional |

---

## 📁 Section 3: Chart Interactions

| Test ID | Test Description | Expected Outcome |
|--------|------------------|------------------|
| TC009  | Hover over a data point | Tooltip displays exact value and date |
| TC010  | Upload multiple reports for the same patient | Chart updates to show trends over time |
| TC011  | Compare two biomarkers on the same chart | Both lines render with correct labels and separate colors |

---

## 📁 Section 4: Interface Features

| Test ID | Test Description | Expected Outcome |
|--------|------------------|------------------|
| TC012  | Button to upload sample data | Dashboard populates with sample report when clicked |
| TC013  | Bottom-left display panel | Displays summary: Report date, abnormal count, etc. |
| TC014  | Bottom info under chart | Shows clinical ranges and last update time |
| TC015  | Scroll or zoom charts (if supported) | Interactions behave as intended with no visual glitches |

---

## 📁 Section 5: Error Handling & Validation

| Test ID | Test Description | Expected Outcome |
|--------|------------------|------------------|
| TC016  | Corrupted PDF file | Error message displayed and no crash occurs |
| TC017  | Backend API returns empty response | UI handles it gracefully and informs the user |
| TC018  | Timeout while uploading | Upload spinner appears; timeout message after delay |
| TC019  | Missing clinical ranges for a biomarker | UI shows "Range Not Available" text below chart |

---

## 📁 Section 6: Performance & Accessibility

| Test ID | Test Description | Expected Outcome |
|--------|------------------|------------------|
| TC020  | Load time for large reports | Dashboard initializes within 3 seconds |
| TC021  | Keyboard navigation on buttons and dropdowns | Accessible via Tab/Shift+Tab |
| TC022  | Screen reader accessibility check | ARIA labels and alt-text available for major UI elements |

---

**Note:** This document is meant to be iteratively updated as new features are added or changed in the dashboard.

