# Transport Member Bulk Import - Quick Start Guide

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
path('transport/members/import/', views.bulk_transport_member_import, name='bulk_transport_member_import'),
path('transport/members/import/template/', views.download_transport_member_import_template, name='download_transport_member_import_template'),
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

**Copy all 4 functions from `bulk_transport_member_import_views.py` to the end of your `views.py`:**

1. `download_transport_member_import_template()` - Lines 33-140
2. `bulk_transport_member_import()` - Lines 144-243
3. `parse_transport_member_excel_file()` - Lines 246-361
4. `parse_transport_member_csv_file()` - Lines 364-456

---

### Step 4: Restart Server (30 seconds)

```bash
python manage.py runserver
```

---

### Step 5: Test It! (1 minute)

1. **Go to:** `http://127.0.0.1:8000/student-management/transport/members/`

2. **Click:** 📊 Bulk Import button

3. **Download template** (Excel or CSV)

4. **Fill template** with member data:
   - Required: student_id, route_id
   - Optional: vehicle_id, pickup, dropoff, joined_at, note

5. **Upload file** and click "Preview & Validate"

6. **Confirm & Import** - Done! ✅

---

## What's Already Done ✅

- ✅ Templates created in `templates/student_management/transport/`
- ✅ Bulk Import button added to member list page
- ✅ All view function code ready in `bulk_transport_member_import_views.py`
- ✅ Complete documentation (this file)

---

## Template Format

### Required Fields (2)

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| student_id | Integer | 1 | Database ID of the student |
| route_id | Integer | 1 | Database ID of the transport route |

### Optional Fields (5)

| Field | Type | Example | Default | Description |
|-------|------|---------|---------|-------------|
| vehicle_id | Integer | 1 | None | Database ID of assigned vehicle |
| pickup | Text | "Mirpur 10 Circle" | "" | Pickup point location |
| dropoff | Text | "School Main Gate" | "" | Drop-off point location |
| joined_at | Date | 2024-01-15 | Today | Date format: YYYY-MM-DD |
| note | Text | "Morning route" | "" | Additional notes |

---

## Features

✅ Download formatted Excel/CSV template with instructions
✅ Upload and validate bulk transport member data
✅ Preview members before importing with full details
✅ Detailed error reporting with specific row numbers
✅ Support for Excel (.xlsx) and CSV formats
✅ Professional glassmorphism UI matching transport theme
✅ Automatic validation of student, route, and vehicle IDs
✅ Duplicate membership detection
✅ Date format validation

---

## Validation Rules

1. **Student ID** - Required, must exist in database, no duplicate memberships
2. **Route ID** - Required, must exist in database
3. **Vehicle ID** - Optional, must exist in database if provided
4. **Pickup Point** - Optional, any text
5. **Drop Point** - Optional, any text
6. **Joined Date** - Optional, must be in YYYY-MM-DD format
7. **Note** - Optional, any text

---

## Examples

### Good Examples:

| student_id | route_id | vehicle_id | pickup | dropoff | joined_at | note |
|------------|----------|------------|--------|---------|-----------|------|
| 1 | 1 | 1 | Mirpur 10 Circle | School Main Gate | 2024-01-15 | Morning route |
| 2 | 1 | 1 | Mirpur 12 | School Main Gate | 2024-01-15 | Same route as student #1 |
| 3 | 2 |  | Uttara Sector 7 | School Campus | 2024-02-01 | No vehicle assigned yet |
| 4 | 2 | 2 | Uttara Sector 9 | School Campus |  | Use today's date |

### Bad Examples (with errors):

| Issue | Example | Error |
|-------|---------|-------|
| Missing student_id | student_id="" | "Student ID is required" |
| Missing route_id | route_id="" | "Route ID is required" |
| Invalid student_id | student_id="999" | "Student with ID 999 not found" |
| Invalid route_id | route_id="999" | "Route with ID 999 not found" |
| Invalid vehicle_id | vehicle_id="999" | "Vehicle with ID 999 not found" |
| Invalid date | joined_at="01/15/2024" | "Invalid date format. Use YYYY-MM-DD" |
| Duplicate membership | student_id="1" (already member) | "Student already has transport membership" |

---

## Troubleshooting

### Issue: "openpyxl is not installed"

**Solution:**
```bash
pip install openpyxl
```

### Issue: NoReverseMatch for 'bulk_transport_member_import'

**Solution:** Make sure you added both URL patterns to `urls.py`

### Issue: "Student with ID X not found"

**Solution:** Use the correct student database ID. Check your student list for valid IDs.

### Issue: "Route with ID X not found"

**Solution:** Use the correct route database ID from your routes list. Use ID, not route name.

### Issue: "Student already has transport membership"

**Solution:** Each student can only have one transport membership. Remove duplicate or update existing membership instead.

### Issue: "Invalid date format for joined_at"

**Solution:** Use YYYY-MM-DD format (e.g., 2024-01-15). Or leave blank to use today's date.

---

## Tips

1. **Get Student IDs:** Go to student list and note the ID numbers you need
2. **Get Route IDs:** Check your routes list for the correct route database IDs
3. **Get Vehicle IDs:** If assigning vehicles, check your vehicles list for IDs
4. **Pickup/Dropoff:** Be specific with locations (e.g., "Mirpur 10 Circle" instead of just "Mirpur")
5. **Date Format:** Always use YYYY-MM-DD format, or leave blank for today's date
6. **Delete Sample Row:** Remember to delete row 10 (sample data) before uploading
7. **One Membership:** Students can only have one transport membership at a time

---

## How to Find Database IDs

### Student IDs:
1. Go to Students List in your admin panel
2. Note the ID numbers (usually shown in the list or URL)
3. Or check database directly: `Student.objects.all().values('id', 'first_name', 'last_name')`

### Route IDs:
1. Go to Transport Routes List
2. Note the route ID numbers
3. Or check database: `TransportRoute.objects.all().values('id', 'name')`

### Vehicle IDs:
1. Go to Vehicles List
2. Note the vehicle ID numbers
3. Or check database: `Vehicle.objects.all().values('id', 'vehicle_number')`

---

## Need Help?

See complete code:
- `bulk_transport_member_import_views.py` - All view function code with comments

---

**Total Setup Time: ~5 minutes**
**Difficulty: Easy (copy-paste)**
**Status: Production-ready** ✅
