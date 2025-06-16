# EcoTown Health Dashboard – API Documentation

This document outlines the API endpoints for the backend Flask server that processes PDF uploads and returns biomarker data.

---

## 📤 POST `/upload`

### Description:
Accepts a PDF file via `multipart/form-data`, processes it, and returns extracted biomarker data in JSON format.

### Request Format:

- **Method**: POST
- **Content-Type**: multipart/form-data
- **File Field**: `report` (should be a `.pdf` file)

### Sample `curl` Command:

```bash
curl -X POST http://localhost:5000/upload   -F "report=@sample_lab_report.pdf"
```

### Success Response (`200 OK`):

```json
{
  "Hemoglobin": { "value": 13.8, "unit": "g/dL" },
  "WBC": { "value": 7000, "unit": "cells/mcL" },
  "Cholesterol": { "value": 180, "unit": "mg/dL" }
}
```

### Error Responses:
- `400 Bad Request`: No file uploaded or incorrect format
- `415 Unsupported Media Type`: File is not a PDF
- `500 Internal Server Error`: Unexpected parsing or server error

---

## 🏠 GET `/`

(Optional if HTML is served via Flask)

- Renders the main frontend dashboard (`index.html`).
- Used only if the app is structured as a full-stack Flask application.

---

## Notes:

- All biomarker parsing is done in-memory using `pdfplumber`.
- No persistent user data or uploaded files are stored on the server.