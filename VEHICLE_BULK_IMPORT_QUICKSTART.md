# Vehicle Bulk Import - Quick Start Guide

## 5-Minute Setup ⚡

### Step 1: Install Package (30 seconds)

```bash
pip install openpyxl
```

---

### Step 2: Add URL Patterns (1 minute)

**File:** `student_management/urls.py`

Add these 2 lines:

```python
path('transport/vehicles/import/', views.bulk_vehicle_import, name='bulk_vehicle_import'),
path('transport/vehicles/import/template/', views.download_vehicle_import_template, name='download_vehicle_import_template'),
```

---

### Step 3: Add View Functions (2 minutes)

**File:** `student_management/views.py`

**Add imports at the top:**

```python
import csv
import io
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

# For Excel support
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
```

**Copy all 4 functions from `bulk_vehicle_import_views.py` to the end of your `views.py`:**

1. `download_vehicle_import_template()` - Lines 32-148
2. `bulk_vehicle_import()` - Lines 152-251
3. `parse_vehicle_excel_file()` - Lines 254-395
4. `parse_vehicle_csv_file()` - Lines 398-519

---

### Step 4: Restart Server (30 seconds)

```bash
python manage.py runserver
```

---

### Step 5: Test It! (1 minute)

1. **Go to:** `http://127.0.0.1:8000/student-management/transport/vehicles/`

2. **Click:** 📊 Bulk Import button

3. **Download template** (Excel or CSV)

4. **Fill template** with vehicle data:
   - Required: vehicle_number, vehicle_model, capacity
   - Optional: vehicle_type, fuel_type, status, etc.

5. **Upload file** and click "Preview & Validate"

6. **Confirm & Import** - Done! ✅

---

## What's Already Done ✅

- ✅ Templates created in `templates/student_management/transport/`
- ✅ Bulk Import button added to vehicle list page
- ✅ All view function code ready in `bulk_vehicle_import_views.py`
- ✅ Complete documentation (this file)

---

## Template Format

### Required Fields (3)

| Field | Type | Example |
|-------|------|---------|
| vehicle_number | Text (Unique) | "DH-12-3456" |
| vehicle_model | Text | "Tata LP 909" |
| capacity | Integer | 45 |

### Optional Fields (11)

| Field | Type | Example | Default |
|-------|------|---------|---------|
| vehicle_type | Text | "Bus" | "Bus" |
| fuel_type | Text | "diesel" | "diesel" |
| manufacture_year | Integer | 2020 | null |
| registration_date | Date (YYYY-MM-DD) | "2024-11-19" | null |
| insurance_expiry | Date (YYYY-MM-DD) | "2025-11-19" | null |
| fitness_certificate_expiry | Date (YYYY-MM-DD) | "2025-05-19" | null |
| last_service_date | Date (YYYY-MM-DD) | "2024-11-01" | null |
| next_service_date | Date (YYYY-MM-DD) | "2025-02-01" | null |
| status | Text | "active" | "active" |
| gps_device_id | Text | "GPS-001" | "" |
| notes | Text | "School bus for Route 1" | "" |

### Valid Values

**vehicle_type:** Bus, Van, Car (or any custom type)

**fuel_type:** petrol, diesel, cng, electric

**status:** active, maintenance, inactive

---

## Features

✅ Download formatted Excel/CSV template with instructions
✅ Upload and validate bulk vehicle data
✅ Preview vehicles before importing with full details
✅ Detailed error reporting with specific row numbers
✅ Support for Excel (.xlsx) and CSV formats
✅ Professional glassmorphism UI matching transport theme
✅ Duplicate detection (vehicle number uniqueness)
✅ Data type validation (integers, dates, choices)

---

## Validation Rules

1. **Vehicle Number** - Must be unique across all vehicles
2. **Vehicle Model** - Required, any text
3. **Capacity** - Required, must be a positive integer
4. **Status** - Must be one of: active, maintenance, inactive
5. **Fuel Type** - Must be one of: petrol, diesel, cng, electric
6. **Dates** - Must be in YYYY-MM-DD format
7. **Manufacture Year** - Must be a 4-digit year (e.g., 2020)
8. **No duplicates** - Vehicle number must not already exist in database

---

## Troubleshooting

### Issue: "openpyxl is not installed"

**Solution:**
```bash
pip install openpyxl
```

### Issue: NoReverseMatch for 'bulk_vehicle_import'

**Solution:** Make sure you added both URL patterns to `urls.py`

### Issue: "Vehicle number XXX already exists"

**Solution:** Each vehicle number must be unique. Use different vehicle numbers or remove duplicates from your import file.

### Issue: "Capacity must be a valid integer"

**Solution:** Enter whole numbers only for capacity (e.g., 45, 50, 60).

### Issue: "Invalid status" or "Invalid fuel_type"

**Solution:** Use only the valid values listed above (lowercase).

### Issue: "Date must be in YYYY-MM-DD format"

**Solution:** Format all dates as YYYY-MM-DD (e.g., 2024-11-19).

---

## Need Help?

See complete documentation:
- `bulk_vehicle_import_views.py` - All view function code with comments

---

**Total Setup Time: ~5 minutes**
**Difficulty: Easy (copy-paste)**
**Status: Production-ready** ✅
