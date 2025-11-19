# Class Section Bulk Import - Quick Start Guide

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
path('academic/sections/import/', views.bulk_section_import, name='bulk_section_import'),
path('academic/sections/import/template/', views.download_section_import_template, name='download_section_import_template'),
```

---

### Step 3: Add View Functions (2 minutes)

**File:** `student_management/views.py`

**Add imports at the top:**

```python
import csv
import io
from decimal import Decimal, InvalidOperation

# For Excel support
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
```

**Copy all 4 functions from `bulk_section_import_views.py` to the end of your `views.py`:**

1. `download_section_import_template()` - Lines 32-134
2. `bulk_section_import()` - Lines 138-238
3. `parse_section_excel_file()` - Lines 241-356
4. `parse_section_csv_file()` - Lines 359-471

---

### Step 4: Restart Server (30 seconds)

```bash
python manage.py runserver
```

---

### Step 5: Test It! (1 minute)

1. **Go to:** `http://127.0.0.1:8000/student-management/academic/sections/`

2. **Click:** 📊 Bulk Import button

3. **Download template** (Excel or CSV)

4. **Fill template** with section data:
   - Required: academic_class_id, name
   - Optional: capacity, room_number, class_teacher_id, is_active

5. **Upload file** and click "Preview & Validate"

6. **Confirm & Import** - Done! ✅

---

## What's Already Done ✅

- ✅ Templates created in `templates/student_management/academic/`
- ✅ Section list page with Bulk Import button
- ✅ All view function code ready in `bulk_section_import_views.py`
- ✅ Complete documentation (this file)

---

## Template Format

### Required Fields (2)

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| academic_class_id | Integer | 1 | Database ID of the academic class |
| name | Text | "A" | Section name (e.g., "A", "B", "Morning") |

### Optional Fields (4)

| Field | Type | Example | Default | Description |
|-------|------|---------|---------|-------------|
| capacity | Integer | 40 | None | Maximum number of students |
| room_number | Text | "Room 101" | "" | Room number or name |
| class_teacher_id | Integer | 1 | None | Database ID of the class teacher |
| is_active | Boolean | true | true | Use "true" or "false" |

---

## Features

✅ Download formatted Excel/CSV template with instructions
✅ Upload and validate bulk section data
✅ Preview sections before importing with full details
✅ Detailed error reporting with specific row numbers
✅ Support for Excel (.xlsx) and CSV formats
✅ Professional glassmorphism UI matching academic theme
✅ Automatic validation of academic class and teacher IDs
✅ Duplicate section detection (per class)
✅ Capacity validation

---

## Validation Rules

1. **Academic Class ID** - Required, must exist in database
2. **Section Name** - Required, must be unique within each class
3. **Capacity** - Optional, must be a positive integer if provided
4. **Room Number** - Optional, any text
5. **Class Teacher ID** - Optional, must exist in database if provided
6. **Is Active** - Optional, must be "true" or "false" (default: true)

---

## Examples

### Good Examples:

| academic_class_id | name | capacity | room_number | class_teacher_id | is_active |
|-------------------|------|----------|-------------|------------------|-----------|
| 1 | A | 40 | Room 101 | 1 | true |
| 1 | B | 40 | Room 102 | 2 | true |
| 2 | Morning | 35 | Room 201 | 3 | true |
| 2 | Evening | 35 | Room 202 |  | true |
| 3 | A |  | Lab 1 | 4 | false |

### Bad Examples (with errors):

| Issue | Example | Error |
|-------|---------|-------|
| Missing academic_class_id | academic_class_id="" | "Academic Class ID is required" |
| Missing name | name="" | "Section name is required" |
| Invalid academic_class_id | academic_class_id="999" | "Academic Class with ID 999 not found" |
| Invalid class_teacher_id | class_teacher_id="999" | "Teacher with ID 999 not found" |
| Invalid capacity | capacity="-5" | "Capacity must be a positive number" |
| Invalid is_active | is_active="maybe" | "is_active must be 'true' or 'false'" |
| Duplicate section | name="A" (for same class) | "Section 'A' already exists for this class" |

---

## Troubleshooting

### Issue: "openpyxl is not installed"

**Solution:**
```bash
pip install openpyxl
```

### Issue: NoReverseMatch for 'bulk_section_import'

**Solution:** Make sure you added both URL patterns to `urls.py`

### Issue: "Academic Class with ID X not found"

**Solution:** Use the correct academic class database ID. Check your class list for valid IDs.

### Issue: "Section 'X' already exists for this class"

**Solution:** Section names must be unique within each class. Use different names or update existing sections.

### Issue: "Capacity must be a positive number"

**Solution:** If providing capacity, use only positive integers (e.g., 30, 40, 50). Leave blank if not needed.

### Issue: "Teacher with ID X not found"

**Solution:** Use the correct teacher database ID from your teacher list. Use ID, not teacher name. Or leave blank if not assigning a teacher.

### Issue: "is_active must be 'true' or 'false'"

**Solution:** Use only "true" or "false" (lowercase). Or leave blank to default to "true".

---

## Tips

1. **Get Class IDs:** Go to academic class list and note the ID numbers you need
2. **Get Teacher IDs:** Check your teacher list for the correct teacher database IDs
3. **Section Names:** Use simple names like "A", "B", "C" or "Morning", "Evening"
4. **Room Numbers:** Be specific (e.g., "Room 101", "Lab A", "Building 2 - Room 305")
5. **Capacity:** Common values are 30, 35, 40, 45, 50 students per section
6. **Delete Sample Row:** Remember to delete row 10 (sample data) before uploading
7. **Unique Names:** Section names must be unique within each class

---

## How to Find Database IDs

### Academic Class IDs:
1. Go to Academic Classes List in your admin panel
2. Note the ID numbers (usually shown in the list or URL)
3. Or check database directly: `AcademicClass.objects.all().values('id', 'class_name')`

### Teacher IDs:
1. Go to Teachers List
2. Note the teacher ID numbers
3. Or check database: `Teacher.objects.all().values('id', 'first_name', 'last_name')`

---

## Common Use Cases

### Example 1: Create sections for Grade 10
```
academic_class_id: 10 (Grade 10 class ID)
Sections: A, B, C, D
Capacity: 40 each
Room Numbers: Room 301, Room 302, Room 303, Room 304
```

### Example 2: Create shift-based sections
```
academic_class_id: 5 (Class 5 ID)
Sections: Morning, Evening
Capacity: 35 each
Room Numbers: Room 101, Room 102
```

### Example 3: Create specialized sections
```
academic_class_id: 12 (Grade 12 ID)
Sections: Science, Commerce, Arts
Capacity: 30, 35, 25
Room Numbers: Lab 1, Room 401, Room 402
```

---

## Sample Template Data

```csv
academic_class_id,name,capacity,room_number,class_teacher_id,is_active
1,A,40,Room 101,1,true
1,B,40,Room 102,2,true
1,C,40,Room 103,3,true
2,Morning,35,Room 201,4,true
2,Evening,35,Room 202,5,true
3,Science,30,Lab 1,6,true
3,Commerce,35,Room 301,7,true
3,Arts,30,Room 302,8,true
```

---

## Need Help?

See complete code:
- `bulk_section_import_views.py` - All view function code with comments

---

**Total Setup Time: ~5 minutes**
**Difficulty: Easy (copy-paste)**
**Status: Production-ready** ✅
