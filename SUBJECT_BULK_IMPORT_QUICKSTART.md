# Subject Bulk Import - Quick Start Guide

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
path('academic/subjects/import/', views.bulk_subject_import, name='bulk_subject_import'),
path('academic/subjects/import/template/', views.download_subject_import_template, name='download_subject_import_template'),
```

---

### Step 3: Add View Functions (2 minutes)

**File:** `student_management/views.py`

**Add imports at the top:**

```python
import csv
import io

# For Excel support
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
```

**Copy all 4 functions from `bulk_subject_import_views.py` to the end of your `views.py`:**

1. `download_subject_import_template()` - Lines 32-139
2. `bulk_subject_import()` - Lines 143-235
3. `parse_subject_excel_file()` - Lines 238-336
4. `parse_subject_csv_file()` - Lines 339-429

---

### Step 4: Restart Server (30 seconds)

```bash
python manage.py runserver
```

---

### Step 5: Test It! (1 minute)

1. **Go to:** `http://127.0.0.1:8000/student-management/academic/subjects/`

2. **Click:** 📊 Bulk Import button

3. **Download template** (Excel or CSV)

4. **Fill template** with subject data:
   - Required: name
   - Optional: code, description, subject_type, is_active

5. **Upload file** and click "Preview & Validate"

6. **Confirm & Import** - Done! ✅

---

## What's Already Done ✅

- ✅ Templates created in `templates/student_management/academic/`
- ✅ Subject list page with Bulk Import button
- ✅ All view function code ready in `bulk_subject_import_views.py`
- ✅ Complete documentation (this file)

---

## Template Format

### Required Fields (1)

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| name | Text | "Mathematics" | Subject name |

### Optional Fields (4)

| Field | Type | Example | Default | Description |
|-------|------|---------|---------|-------------|
| code | Text | "MATH101" | "" | Subject code (unique) |
| description | Text | "Basic Mathematics..." | "" | Subject description |
| subject_type | Text | "Theory" | "Theory" | Theory, Practical, Lab, or Both |
| is_active | Boolean | true | true | Use "true" or "false" |

---

## Features

✅ Download formatted Excel/CSV template with instructions
✅ Upload and validate bulk subject data
✅ Preview subjects before importing with full details
✅ Detailed error reporting with specific row numbers
✅ Support for Excel (.xlsx) and CSV formats
✅ Professional glassmorphism UI matching academic theme
✅ Automatic duplicate detection (name and code)
✅ Subject type validation
✅ Status management (active/inactive)

---

## Validation Rules

1. **Subject Name** - Required, must be unique within institution
2. **Subject Code** - Optional, must be unique if provided
3. **Description** - Optional, any text
4. **Subject Type** - Optional, must be: Theory, Practical, Lab, or Both (default: Theory)
5. **Is Active** - Optional, must be "true" or "false" (default: true)

---

## Examples

### Good Examples:

| name | code | description | subject_type | is_active |
|------|------|-------------|--------------|-----------|
| Mathematics | MATH101 | Basic Mathematics for Grade 10 | Theory | true |
| Physics | PHY201 | Physics with Lab sessions | Both | true |
| Computer Lab | CS301 | Practical computer skills | Practical | true |
| Chemistry Lab | CHEM101L | Chemistry laboratory | Lab | true |
| English | ENG101 | English Language and Literature | Theory | true |
| Biology |  | General Biology | Theory | false |

### Bad Examples (with errors):

| Issue | Example | Error |
|-------|---------|-------|
| Missing name | name="" | "Subject name is required" |
| Duplicate name | name="Mathematics" (exists) | "Subject 'Mathematics' already exists" |
| Duplicate code | code="MATH101" (exists) | "Subject code 'MATH101' already exists" |
| Invalid subject_type | subject_type="Online" | "subject_type must be: Theory, Practical, Lab, or Both" |
| Invalid is_active | is_active="maybe" | "is_active must be 'true' or 'false'" |

---

## Troubleshooting

### Issue: "openpyxl is not installed"

**Solution:**
```bash
pip install openpyxl
```

### Issue: NoReverseMatch for 'bulk_subject_import'

**Solution:** Make sure you added both URL patterns to `urls.py`

### Issue: "Subject 'X' already exists"

**Solution:** Subject names must be unique within your institution. Use different names or update existing subjects.

### Issue: "Subject code 'X' already exists"

**Solution:** If providing subject codes, they must be unique. Use different codes or leave blank.

### Issue: "subject_type must be: Theory, Practical, Lab, or Both"

**Solution:** Use only these exact values (case-insensitive). Leave blank for Theory (default).

### Issue: "is_active must be 'true' or 'false'"

**Solution:** Use only "true" or "false" (lowercase). Or leave blank to default to "true".

---

## Tips

1. **Subject Names:** Use clear, official names like "Mathematics", "English", "Physics"
2. **Subject Codes:** Follow a consistent format (e.g., "MATH101", "ENG201", "PHY301")
3. **Descriptions:** Be specific about what the subject covers
4. **Subject Types:**
   - **Theory:** Classroom-based subjects (Math, English, History)
   - **Practical:** Hands-on subjects (Art, Music, PE)
   - **Lab:** Laboratory subjects (Chemistry Lab, Physics Lab)
   - **Both:** Subjects with theory and practical components
5. **Delete Sample Row:** Remember to delete row 10 (sample data) before uploading
6. **Unique Names:** Each subject name must be unique across your institution

---

## Common Use Cases

### Example 1: Import core subjects for a grade
```csv
name,code,description,subject_type,is_active
Mathematics,MATH10,Mathematics for Grade 10,Theory,true
English,ENG10,English Language and Literature,Theory,true
Physics,PHY10,Physics for Grade 10,Theory,true
Chemistry,CHEM10,Chemistry for Grade 10,Theory,true
Biology,BIO10,Biology for Grade 10,Theory,true
```

### Example 2: Import subjects with lab components
```csv
name,code,description,subject_type,is_active
Chemistry,CHEM301,General Chemistry,Theory,true
Chemistry Lab,CHEM301L,Chemistry Laboratory,Lab,true
Physics,PHY301,General Physics,Theory,true
Physics Lab,PHY301L,Physics Laboratory,Lab,true
```

### Example 3: Import practical subjects
```csv
name,code,description,subject_type,is_active
Computer Science,CS101,Introduction to Programming,Both,true
Art & Design,ART101,Creative Art and Design,Practical,true
Physical Education,PE101,Physical Education and Sports,Practical,true
Music,MUS101,Music Theory and Practice,Both,true
```

---

## Sample Template Data

```csv
name,code,description,subject_type,is_active
Mathematics,MATH101,Basic Mathematics for Grade 10,Theory,true
English,ENG201,English Language,Theory,true
Physics,PHY301,Physics with experiments,Both,true
Chemistry Lab,CHEM101L,Chemistry Laboratory,Lab,true
Computer Science,CS401,Programming and algorithms,Practical,true
Biology,BIO101,General Biology,Theory,true
History,HIST201,World History,Theory,true
Geography,GEO201,Physical and Human Geography,Theory,true
Art,ART101,Creative Arts,Practical,true
Music,MUS101,Music Theory,Both,true
```

---

## Subject Type Guidelines

### Theory
- Classroom-based subjects
- Primarily lecture and discussion
- Examples: Mathematics, English, History, Economics

### Practical
- Hands-on activities
- Skills-based learning
- Examples: Art, Music, Physical Education, Typing

### Lab
- Laboratory-based subjects
- Experiments and observations
- Examples: Chemistry Lab, Physics Lab, Biology Lab, Computer Lab

### Both
- Combination of theory and practical
- Includes both classroom and hands-on components
- Examples: Computer Science, Food & Nutrition, Design & Technology

---

## Subject Naming Conventions

### Good Names:
- Mathematics
- English Language
- Physics
- Chemistry
- Computer Science
- Physical Education
- History
- Biology

### Avoid:
- Math (use "Mathematics")
- Comp Sci (use "Computer Science")
- PE (use "Physical Education")
- Lang (be specific: "English Language", "French Language")

---

## Subject Code Patterns

### Common Patterns:
- **Letter + Number:** MATH101, ENG201, PHY301
- **Department Code + Level:** CS-101, BIO-201, CHEM-301
- **Grade Based:** MATH10 (Grade 10 Math), ENG11 (Grade 11 English)
- **Lab Suffix:** CHEM101L (Chemistry Lab), PHY201L (Physics Lab)

### Tips:
- Be consistent across all subjects
- Use 3-4 letters for subject abbreviation
- Use 2-3 digits for level/grade
- Add "L" suffix for lab sections

---

## Need Help?

See complete code:
- `bulk_subject_import_views.py` - All view function code with comments

---

**Total Setup Time: ~5 minutes**
**Difficulty: Easy (copy-paste)**
**Status: Production-ready** ✅
