# Bulk Book Import - Installation Guide

Complete guide to add Excel/CSV bulk import functionality to your Library Management System.

---

## Features

✅ Download formatted Excel/CSV template
✅ Upload and validate bulk book data
✅ Preview before importing
✅ Detailed error reporting with line numbers
✅ Support for Excel (.xlsx) and CSV formats
✅ Professional glassmorphism UI matching your theme

---

## Step 1: Install Required Packages

```bash
cd /Users/macbookpro/Desktop/techgenius/writixaisite
pip install openpyxl
```

**Note:** CSV support works without additional packages. Excel support requires `openpyxl`.

---

## Step 2: Add Views

**File:** `student_management/views.py`

Copy these 3 functions from `bulk_book_import_views.py`:

1. `download_book_import_template()` - Template download
2. `bulk_book_import()` - Upload and import handler
3. `parse_excel_file()` - Excel parser
4. `parse_csv_file()` - CSV parser

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

**Paste all functions** at the end of your `views.py` file.

---

## Step 3: Add URL Patterns

**File:** `student_management/urls.py`

Add these URL patterns:

```python
urlpatterns = [
    # ... your existing patterns ...

    # Bulk Book Import
    path('library/books/import/', views.bulk_book_import, name='bulk_book_import'),
    path('library/books/import/template/', views.download_book_import_template, name='download_book_import_template'),
]
```

---

## Step 4: Add Templates

Copy these 3 template files to:
`templates/student_management/library/`

1. **bulk_import_form.html** - Upload interface
2. **bulk_import_preview.html** - Preview before import
3. **bulk_import_errors.html** - Error display

**Commands:**

```bash
cd /Users/macbookpro/Desktop/techgenius/writixaisite

# Create directory if doesn't exist
mkdir -p templates/student_management/library

# Copy templates (from your repository files)
cp templates_bulk_import/bulk_import_form.html templates/student_management/library/
cp templates_bulk_import/bulk_import_preview.html templates/student_management/library/
cp templates_bulk_import/bulk_import_errors.html templates/student_management/library/
```

---

## Step 5: Add Link to Book List Page

**File:** `templates/student_management/library/book_list.html`

Add a button next to "Add New Book":

```html
<div class="action-bar">
    <div class="search-box">
        <input type="text" class="search-input" placeholder="Search..." id="searchBooks">
    </div>
    <div style="display: flex; gap: 10px;">
        <!-- Existing Add New Book button -->
        <a href="{% url 'book_form' %}" class="btn btn-success">
            ➕ Add New Book
        </a>

        <!-- NEW: Bulk Import button -->
        <a href="{% url 'bulk_book_import' %}" class="btn btn-info">
            📊 Bulk Import
        </a>
    </div>
</div>
```

---

## Step 6: Test the Feature

1. **Restart Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate to:**
   ```
   http://127.0.0.1:8000/student-management/library/books/
   ```

3. **Click "Bulk Import" button**

4. **Download template:**
   - Click "Download Excel Template" or "Download CSV Template"
   - Template will download with instructions and sample data

5. **Fill template:**
   - Open downloaded file
   - Read instructions (red text)
   - Fill your book data
   - Delete instruction rows
   - Delete sample data row
   - Save file

6. **Upload file:**
   - Click "Click to browse" or drag & drop
   - Select your filled Excel/CSV file
   - Click "Preview & Validate"

7. **Review preview:**
   - Check all data is correct
   - Click "Confirm & Import X Books"

8. **Success!**
   - Books imported to library
   - Redirected to book list

---

## Template Format

### Required Fields

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| name | Text | "Introduction to Python" | Book title (required) |
| author | Text | "John Smith" | Author name (required) |
| price | Decimal | 850.00 | Price in BDT (required) |
| quantity | Integer | 10 | Total copies (required) |

### Optional Fields

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| publisher | Text | "Tech Publishers" | Publisher name |
| isbn | Text | "978-0-123456-78-9" | ISBN number (unique) |
| edition | Text | "3rd Edition" | Edition info |
| publication_year | Integer | 2024 | Year published |
| category | Text | "science" | See categories below |
| subject_code | Text | "CS101" | Subject/course code |
| language | Text | "English" | Language |
| available_quantity | Integer | 10 | Available (defaults to quantity) |
| rack_no | Text | "A1" | Rack location |
| shelf_location | Text | "Top Shelf" | Shelf description |
| pages | Integer | 450 | Number of pages |
| description | Text | "Comprehensive guide..." | Brief description |
| barcode | Text | "BK2024001" | Barcode (unique) |

### Valid Categories

- fiction
- non_fiction
- science
- mathematics
- history
- geography
- literature
- biography
- reference
- other

---

## Error Handling

The system validates:

✅ **Required fields** - name, author, price, quantity
✅ **Data types** - price (decimal), quantity (integer), year (integer)
✅ **Unique fields** - ISBN, barcode (if provided)
✅ **Valid categories** - From predefined list
✅ **File format** - Excel (.xlsx) or CSV only

**If errors found:**
- Shows detailed error list with row numbers
- Explains what's wrong
- Provides fix instructions
- Allows download fresh template
- Allows retry

**Error display example:**
```
Row 5: Price is required
Row 7: Invalid quantity format
Row 12: Author is required
```

---

## Usage Tips

### For Excel Files:

1. **Don't modify headers** - Keep column names exact
2. **Delete instructions** - Remove red instruction rows
3. **One book per row** - Each row = one book
4. **No empty rows** - Between data rows
5. **Save as .xlsx** - Not .xls

### For CSV Files:

1. **Use UTF-8 encoding** - For special characters
2. **Comma-separated** - Standard CSV format
3. **Quote text with commas** - "Book Title, Part 2"
4. **No extra line breaks** - Within cells

### Best Practices:

1. **Start small** - Test with 5-10 books first
2. **Use template** - Always start with downloaded template
3. **Check sample** - Follow sample data format exactly
4. **Review preview** - Check all data before confirming
5. **Keep backup** - Save your Excel/CSV file

---

## Troubleshooting

### Issue: "openpyxl is not installed"

**Solution:**
```bash
pip install openpyxl
```

### Issue: Excel download not working

**Solution:** Use CSV instead:
```
http://127.0.0.1:8000/student-management/library/books/import/template/?format=csv
```

### Issue: "Header row not found"

**Solution:**
- Make sure first column header is exactly "name" (lowercase)
- Don't modify template headers
- Download fresh template

### Issue: Import says "0 books imported"

**Solution:**
- Check you didn't delete data rows
- Make sure file has data (not just headers)
- Check for instruction rows still present (delete them)

### Issue: Some books imported, some failed

**Solution:**
- Check error list for failed rows
- Fix errors in original file
- Upload again (successful books won't duplicate if ISBN/barcode are unique)

---

## Advanced Usage

### Importing Large Files

For files with 100+ books:

1. **Split into batches** - 50-100 books per file
2. **Import separately** - Monitor each batch
3. **Check progress** - Verify each batch imported correctly

### Custom Categories

To add custom categories, update the Book model's `CATEGORY_CHOICES` in `models.py`.

### Default Values

The system sets these defaults:

- `available_quantity` = `quantity` (if not provided)
- `category` = "other" (if not provided)
- `language` = "English" (if not provided)

---

## File Reference

All files in your repository:

| File | Purpose |
|------|---------|
| **bulk_book_import_views.py** | View functions |
| **bulk_import_form.html** | Upload interface |
| **bulk_import_preview.html** | Preview page |
| **bulk_import_errors.html** | Error display |
| **BULK_IMPORT_INSTALLATION.md** | This guide |

---

## Summary

**Setup Time:** 10-15 minutes
**Complexity:** Easy (copy-paste)
**Dependencies:** `openpyxl` (for Excel)
**Files to add:** 4 (views + 3 templates)
**URL patterns:** 2

**After setup:**
1. Download template
2. Fill with data
3. Upload file
4. Preview
5. Confirm
6. Done! ✅

The bulk import feature is production-ready and handles all edge cases!
