# Transport Route Bulk Import - Quick Start Guide

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
path('transport/routes/import/', views.bulk_route_import, name='bulk_route_import'),
path('transport/routes/import/template/', views.download_route_import_template, name='download_route_import_template'),
```

---

### Step 3: Add View Functions (2 minutes)

**File:** `student_management/views.py`

**Add imports at the top:**

```python
import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation

# For Excel support
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
```

**Copy all 4 functions from `bulk_route_import_views.py` to the end of your `views.py`:**

1. `download_route_import_template()` - Lines 32-119
2. `bulk_route_import()` - Lines 123-210
3. `parse_route_excel_file()` - Lines 213-297
4. `parse_route_csv_file()` - Lines 300-380

---

### Step 4: Restart Server (30 seconds)

```bash
python manage.py runserver
```

---

### Step 5: Test It! (1 minute)

1. **Go to:** `http://127.0.0.1:8000/student-management/transport/routes/`

2. **Click:** 📊 Bulk Import button

3. **Download template** (Excel or CSV)

4. **Fill template** with route data:
   - Required: name, start_point, end_point, fare
   - Optional: note

5. **Upload file** and click "Preview & Validate"

6. **Confirm & Import** - Done! ✅

---

## What's Already Done ✅

- ✅ Templates created in `templates/student_management/transport/`
- ✅ Bulk Import button added to route list page
- ✅ All view function code ready in `bulk_route_import_views.py`
- ✅ Complete documentation (this file)

---

## Template Format

### Required Fields (4)

| Field | Type | Example |
|-------|------|---------|
| name | Text | "Route 1 - Mirpur" |
| start_point | Text | "Mirpur 10" |
| end_point | Text | "School Campus" |
| fare | Decimal | 500 or 750.50 |

### Optional Fields (1)

| Field | Type | Example | Default |
|-------|------|---------|---------|
| note | Text | "Morning pickup at 7:00 AM" | "" |

---

## Features

✅ Download formatted Excel/CSV template with instructions
✅ Upload and validate bulk route data
✅ Preview routes before importing with full details
✅ Detailed error reporting with specific row numbers
✅ Support for Excel (.xlsx) and CSV formats
✅ Professional glassmorphism UI matching transport theme
✅ Simple template with minimal required fields
✅ Fare validation (must be positive number)

---

## Validation Rules

1. **Route Name** - Required, any text
2. **Start Point** - Required, starting location
3. **End Point** - Required, ending location (usually "School Campus")
4. **Fare** - Required, must be a positive number (no currency symbols)
5. **Note** - Optional, any additional information

---

## Examples

### Good Examples:

| name | start_point | end_point | fare | note |
|------|-------------|-----------|------|------|
| Route 1 - Mirpur | Mirpur 10 | School Campus | 500 | Morning pickup at 7:00 AM |
| Uttara Route | Uttara Sector 7 | School Campus | 750 | Covers Sectors 5-11 |
| Dhanmondi Route | Dhanmondi 32 | School Campus | 600.50 | Via Shankar |

### Bad Examples (with errors):

| Issue | Example | Error |
|-------|---------|-------|
| Missing name | (empty) | "Route name is required" |
| Missing fare | name="Route 1", fare="" | "Fare is required" |
| Invalid fare | fare="৳500" | "Fare must be a valid number" |
| Negative fare | fare="-100" | "Fare must be a positive number" |

---

## Troubleshooting

### Issue: "openpyxl is not installed"

**Solution:**
```bash
pip install openpyxl
```

### Issue: NoReverseMatch for 'bulk_route_import'

**Solution:** Make sure you added both URL patterns to `urls.py`

### Issue: "Fare must be a valid number"

**Solution:** Enter only numbers (e.g., 500, 750.50). Do not use currency symbols (৳, $, etc.)

### Issue: "Fare must be a positive number"

**Solution:** Fare cannot be negative or zero. Enter a positive amount.

---

## Tips

1. **Route Naming:** Use descriptive names like "Route 1 - Mirpur" or "Uttara Route"
2. **Start Points:** Be specific (e.g., "Mirpur 10" instead of just "Mirpur")
3. **Fare Format:** Use decimal format for precision (e.g., 750.50 instead of 751)
4. **Notes:** Add useful information like timing, areas covered, or special instructions

---

## Need Help?

See complete code:
- `bulk_route_import_views.py` - All view function code with comments

---

**Total Setup Time: ~5 minutes**
**Difficulty: Easy (copy-paste)**
**Status: Production-ready** ✅
