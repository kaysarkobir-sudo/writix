# Fix EBook FieldError: "Cannot resolve keyword 'uploaded_on'"

## The Problem

Your EBook table only has 4 columns:
- id
- title
- description
- file

But the views are trying to use `uploaded_on` which doesn't exist yet.

---

## Solution 1: Quick Fix (5 minutes) ⚡

Update your views to work with the minimal table structure.

### Step 1: Update `ebook_list` view

**File:** `student_management/views.py`

Find the `ebook_list` function (around line 9094) and replace it with:

```python
@login_required
def ebook_list(request):
    """List all e-books - Works with minimal table"""
    # Use 'id' instead of 'uploaded_on' for ordering
    ebooks = EBook.objects.all().order_by('-id')

    # Search (only using fields that exist)
    search = request.GET.get('search', '')
    if search:
        ebooks = ebooks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    context = {
        'ebooks': ebooks,
        'search': search,
        'format_filter': '',
    }

    return render(request, 'student_management/library/ebook_list.html', context)
```

### Step 2: Update `ebook_form` view

Replace your `ebook_form` function with the one from `library_views_quick_fix.py`

### Step 3: Update `library_panel` view

In the `library_panel` function, change this line:
```python
# OLD (line with error):
issues = IssueReturn.objects.select_related('book', 'member__student').all().order_by('-issue_date')[:20]
ebooks = EBook.objects.all().order_by('-uploaded_on')[:12]

# NEW (use 'id' instead):
issues = IssueReturn.objects.select_related('book', 'member__student').all().order_by('-id')[:20]
ebooks = EBook.objects.all().order_by('-id')[:12]
```

### Step 4: Copy simple template

Copy `ebook_form_simple.html` to:
```
/Users/macbookpro/Desktop/techgenius/writixaisite/templates/student_management/library/ebook_form_simple.html
```

### Step 5: Test

Restart server and visit:
```
http://127.0.0.1:8000/student-management/library/ebooks/
```

✓ Should work now!

---

## Solution 2: Full Feature Update (10 minutes) 🚀

Add all missing columns to get full functionality.

### What You'll Get:
- Author field
- Cover images
- Category & format tracking
- File size display
- Page count
- Public/private access control
- Download & view counters
- Upload date tracking
- Uploaded by user tracking

### Steps:

1. **Run the update script:**
   ```bash
   cd /Users/macbookpro/Desktop/techgenius/writixaisite
   python manage.py shell < update_ebook_table.py
   ```

2. **Verify columns added:**
   The script will show you each column as it's added.

3. **Restart server:**
   ```bash
   python manage.py runserver
   ```

4. **Test:**
   Visit the e-books page - now you'll have all the advanced features!

---

## Which Solution Should You Choose?

### Choose Quick Fix if:
- ✓ You just want it to work NOW
- ✓ You don't need advanced features yet
- ✓ Minimal setup (just title, description, file)

### Choose Full Update if:
- ✓ You want all features (categories, formats, download tracking, etc.)
- ✓ You want cover images
- ✓ You want proper date tracking
- ✓ You're building a production system

---

## Complete File Reference

All code files in your repository:

1. **library_views_quick_fix.py** - Updated view functions
2. **ebook_form_simple.html** - Simple form template
3. **update_ebook_table.py** - Table update script

---

## Troubleshooting

### Still getting FieldError?
Make sure you:
1. Replaced ALL occurrences of `.order_by('-uploaded_on')` with `.order_by('-id')`
2. Restarted Django server
3. Cleared browser cache

### After Full Update, views still fail?
If you ran `update_ebook_table.py` and it succeeded, you can use the ORIGINAL view functions from `library_views_complete.py` - they'll work with all the new columns.

---

## Summary

**Quick Fix:** Change 3 lines in views.py, use simple template
**Full Update:** Run one shell script, get all features

Both solutions work - choose based on your needs!
