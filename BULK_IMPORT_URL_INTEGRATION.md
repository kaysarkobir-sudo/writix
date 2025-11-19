# Bulk Import URL Integration

## Add These URL Patterns

**File:** `student_management/urls.py` (or wherever your library URL patterns are)

Add these 2 URL patterns to enable bulk book import:

```python
# Bulk Book Import URLs
path('library/books/import/', views.bulk_book_import, name='bulk_book_import'),
path('library/books/import/template/', views.download_book_import_template, name='download_book_import_template'),
```

---

## Complete Example

If you already have library URLs in your `urls.py`, add these patterns alongside them:

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... your existing patterns ...

    # Library Panel
    path('library/', views.library_panel, name='library_panel'),

    # Books
    path('library/books/', views.book_list, name='book_list'),
    path('library/books/add/', views.book_form, name='book_form'),
    path('library/books/<int:pk>/edit/', views.book_form, name='book_form'),
    path('library/books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # 🆕 NEW: Bulk Book Import
    path('library/books/import/', views.bulk_book_import, name='bulk_book_import'),
    path('library/books/import/template/', views.download_book_import_template, name='download_book_import_template'),

    # ... rest of your library patterns ...
]
```

---

## Add View Functions to views.py

**File:** `student_management/views.py`

Copy these 4 functions from `bulk_book_import_views.py` to your `views.py`:

1. `download_book_import_template(request)` - Line 32-156
2. `bulk_book_import(request)` - Line 160-243
3. `parse_excel_file(uploaded_file)` - Line 246-357
4. `parse_csv_file(uploaded_file)` - Line 360-465

**Add imports at the top of views.py:**

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

**Paste all 4 functions at the end of your `views.py` file.**

---

## Install Required Package

For Excel support, install openpyxl:

```bash
pip install openpyxl
```

**Note:** CSV support works without additional packages.

---

## Verify Setup

After adding URL patterns and view functions:

1. **Restart Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate to book list:**
   ```
   http://127.0.0.1:8000/student-management/library/books/
   ```

3. **You should see:**
   - ✅ "Bulk Import" button (📊) next to "Add New Book"
   - Click it to access bulk import page

4. **Test the workflow:**
   - Download template (Excel or CSV)
   - Fill with sample data
   - Upload file
   - Preview and import

---

## Files Already Set Up

✅ **Templates copied** - All 3 bulk import templates are in:
   - `templates/student_management/library/bulk_import_form.html`
   - `templates/student_management/library/bulk_import_preview.html`
   - `templates/student_management/library/bulk_import_errors.html`

✅ **Button added** - "Bulk Import" button added to `book_list.html`

✅ **View functions ready** - All code available in `bulk_book_import_views.py`

✅ **Documentation** - Complete guide in `BULK_IMPORT_INSTALLATION.md`

---

## Quick Copy-Paste

**Just add these 2 lines to your urls.py:**

```python
path('library/books/import/', views.bulk_book_import, name='bulk_book_import'),
path('library/books/import/template/', views.download_book_import_template, name='download_book_import_template'),
```

**And copy 4 functions from `bulk_book_import_views.py` to `views.py`.**

**Done!** 🎉
