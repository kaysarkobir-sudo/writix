# Quick Fix: E-Book S3 Access WITHOUT AWS Credentials

## Choose Your Solution (Based on Your Needs)

### ⚡ Option A: Public Access (FASTEST - 5 minutes)
**Use if:** E-books can be accessed by anyone with the link
**Security:** Files are public
**Setup:** Very easy

### 🔐 Option B: Login Required (SECURE - 10 minutes)
**Use if:** Only logged-in users should access files
**Security:** Login protected
**Setup:** Easy

---

## Option A: Make Files Public (Recommended) ⚡

### Step 1: Make S3 Bucket Public

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click on bucket: `writixaidbasebackuspaces`
3. Go to **Permissions** tab
4. Click **Edit** on "Block public access"
5. **Uncheck ALL boxes**
6. Click **Save changes**

### Step 2: Add Bucket Policy

Still in **Permissions** tab:

1. Scroll to **Bucket policy**
2. Click **Edit**
3. Paste this:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::writixaidbasebackuspaces/*"
        }
    ]
}
```

4. Click **Save changes**

### Step 3: Fix Database Paths

```bash
cd /Users/macbookpro/Desktop/techgenius/writixaisite
python manage.py shell < fix_ebook_urls_public.py
```

### Step 4: Test

Visit: `http://127.0.0.1:8000/student-management/library/ebooks/`

Click **Read** → Should work! ✅

**Done! No Django changes needed!**

---

## Option B: Login Required Access 🔐

### Step 1: Install Required Package

```bash
pip install requests
```

### Step 2: Add Proxy View

**File:** `student_management/views.py`

Add this function (copy from `ebook_proxy_view.py`):

```python
import requests
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def serve_ebook(request, ebook_id):
    """Serve ebook through Django (login required)"""
    try:
        ebook = get_object_or_404(EBook, id=ebook_id)

        bucket = 'writixaidbasebackuspaces'
        region = 'ap-southeast-1'

        file_path = ebook.file.name
        file_path = file_path.replace(f'{bucket}/{bucket}/', '')
        file_path = file_path.replace(f'{bucket}/', '')

        s3_url = f'https://{bucket}.s3.{region}.amazonaws.com/{file_path}'

        response = requests.get(s3_url, stream=True, timeout=30)

        if response.status_code != 200:
            raise Http404("File not found")

        content_type = response.headers.get('Content-Type', 'application/pdf')
        django_response = HttpResponse(response.content, content_type=content_type)
        django_response['Content-Disposition'] = f'inline; filename="{ebook.title}.pdf"'

        return django_response

    except Exception as e:
        raise Http404(f"Error: {e}")
```

### Step 3: Add URL Pattern

**File:** `student_management/urls.py`

```python
urlpatterns = [
    # ... existing patterns ...
    path('library/ebooks/<int:ebook_id>/view/', views.serve_ebook, name='serve_ebook'),
]
```

### Step 4: Update Template

**File:** `templates/student_management/library/ebook_list.html`

Find this line:
```html
<a href="{{ ebook.file.url }}" target="_blank">📖 Read</a>
```

Replace with:
```html
<a href="{% url 'serve_ebook' ebook.id %}" target="_blank">📖 Read</a>
```

### Step 5: Make S3 Bucket Public

Still need to make bucket public (follow Option A Steps 1-2) because Django needs to fetch files from S3.

### Step 6: Test

Visit: `http://127.0.0.1:8000/student-management/library/ebooks/`

Click **Read** → Should work! ✅

---

## Troubleshooting

### Issue: "File not found" error

**Solution:** Check your S3 bucket region in `views.py`:

```python
region = 'ap-southeast-1'  # Change to your actual region
```

Common regions:
- US East: `us-east-1`
- US West: `us-west-2`
- Asia Pacific (Singapore): `ap-southeast-1`
- Asia Pacific (Mumbai): `ap-south-1`
- Europe (Ireland): `eu-west-1`

Find your region: AWS S3 → Select bucket → Properties → Region

### Issue: "Access Denied"

**Solution:** Make sure you completed the bucket policy step correctly.

### Issue: Still see duplicate path

**Solution:** Run the path fixer again:
```bash
python manage.py shell < fix_ebook_urls_public.py
```

---

## Summary

| What You Need | Option A | Option B |
|---------------|----------|----------|
| AWS Credentials in Django | ❌ No | ❌ No |
| django-storages package | ❌ No | ❌ No |
| Make S3 bucket public | ✅ Yes | ✅ Yes |
| Login required | ❌ No | ✅ Yes |
| Server bandwidth | None | Medium |
| Setup time | 5 min | 10 min |

**Both options avoid putting AWS credentials in your code!**

---

## My Recommendation

**Start with Option A** (Public Access):
1. Quick to implement (5 minutes)
2. No code changes needed
3. Fastest performance
4. Works immediately

**Upgrade to Option B later** if you need:
- Login-based access control
- User tracking
- Download limits

---

## Files Reference

All code is in your repository:

- **ALTERNATIVE_S3_SOLUTIONS.md** - Detailed guide
- **fix_ebook_urls_public.py** - Path fixing script
- **ebook_proxy_view.py** - Complete proxy view code

---

## Next Steps

After fixing:

1. ✅ Test all e-book links
2. ✅ Test upload new e-books
3. ✅ Check download functionality
4. ✅ Verify mobile access

All should work without AWS credentials in Django! 🎉
