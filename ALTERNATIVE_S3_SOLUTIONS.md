# Alternative Solutions for S3 E-Book Access (No AWS Credentials Needed)

## Option 1: Make S3 Files Publicly Accessible (Easiest) ⚡

This is the simplest fix - make your S3 bucket public so files can be accessed without authentication.

### Step 1: Update S3 Bucket Policy

Go to AWS Console → S3 → `writixaidbasebackuspaces` bucket → **Permissions** → **Bucket Policy**

Paste this policy:

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

Click **Save**.

### Step 2: Unblock Public Access

In the same bucket → **Permissions** → **Block public access** → Click **Edit**

Uncheck these:
- ❌ Block all public access
- ❌ Block public access to buckets and objects granted through new public bucket or access point policies

Click **Save changes**.

### Step 3: Fix File URLs in Database

Run this script to use direct S3 URLs (no Django storage needed):

```python
# fix_ebook_urls_public.py
from student_management.models import EBook

bucket_name = 'writixaidbasebackuspaces'
region = 'ap-southeast-1'  # Change to your region

for ebook in EBook.objects.all():
    if ebook.file:
        # Clean path - remove duplicate bucket name
        file_path = ebook.file.name
        file_path = file_path.replace(f'{bucket_name}/{bucket_name}/', '')
        file_path = file_path.replace(f'{bucket_name}/', '')

        # Create direct S3 URL
        direct_url = f'https://{bucket_name}.s3.{region}.amazonaws.com/{file_path}'

        print(f"{ebook.title}: {direct_url}")

        # Store the clean path
        ebook.file.name = file_path
        ebook.save()

print("Done! Files are now using direct S3 URLs")
```

Run it:
```bash
python manage.py shell < fix_ebook_urls_public.py
```

### Step 4: Update Template (Optional)

If you want to use direct URLs in templates, update your `ebook_list.html`:

```html
<!-- Instead of {{ ebook.file.url }} -->
<a href="https://writixaidbasebackuspaces.s3.ap-southeast-1.amazonaws.com/{{ ebook.file.name }}" target="_blank">
    📖 Read
</a>
```

**Pros:**
- ✅ No AWS credentials needed
- ✅ No django-storages needed
- ✅ Files directly accessible
- ✅ Fastest performance

**Cons:**
- ⚠️ Anyone with URL can access files
- ⚠️ No access control

---

## Option 2: Use Django Proxy View (No S3 Configuration)

Create a view that fetches files from S3 and serves them through Django.

### Create a proxy view:

**File:** `student_management/views.py`

```python
import requests
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required

@login_required
def serve_ebook(request, ebook_id):
    """Proxy view to serve e-books from S3 without credentials"""

    try:
        ebook = EBook.objects.get(id=ebook_id)

        # Build direct S3 URL
        bucket = 'writixaidbasebackuspaces'
        region = 'ap-southeast-1'
        file_path = ebook.file.name

        # Remove duplicate bucket name if present
        file_path = file_path.replace(f'{bucket}/{bucket}/', '')
        file_path = file_path.replace(f'{bucket}/', '')

        s3_url = f'https://{bucket}.s3.{region}.amazonaws.com/{file_path}'

        # Fetch file from S3
        response = requests.get(s3_url, stream=True)

        if response.status_code != 200:
            raise Http404("File not found")

        # Determine content type
        content_type = response.headers.get('Content-Type', 'application/octet-stream')

        # Create Django response
        django_response = HttpResponse(response.content, content_type=content_type)
        django_response['Content-Disposition'] = f'inline; filename="{ebook.title}.pdf"'

        return django_response

    except EBook.DoesNotExist:
        raise Http404("E-book not found")
    except Exception as e:
        raise Http404(f"Error loading file: {e}")
```

### Add URL pattern:

**File:** `student_management/urls.py`

```python
urlpatterns = [
    # ... existing patterns ...
    path('library/ebooks/<int:ebook_id>/view/', views.serve_ebook, name='serve_ebook'),
]
```

### Update template links:

**File:** `ebook_list.html`

```html
<!-- Change from: -->
<a href="{{ ebook.file.url }}" target="_blank">📖 Read</a>

<!-- To: -->
<a href="{% url 'serve_ebook' ebook.id %}" target="_blank">📖 Read</a>
```

### Install requests:
```bash
pip install requests
```

**Pros:**
- ✅ No AWS credentials needed
- ✅ Login required (access control)
- ✅ Works with existing setup

**Cons:**
- ⚠️ Slower (goes through Django)
- ⚠️ Uses server bandwidth

---

## Option 3: Store Files Locally (No S3)

Stop using S3 and store files on your local server instead.

### Step 1: Update Settings

**File:** `settings.py`

```python
# REMOVE or COMMENT OUT S3 settings
# AWS_ACCESS_KEY_ID = ...
# AWS_SECRET_ACCESS_KEY = ...
# DEFAULT_FILE_STORAGE = ...

# USE Local file storage instead
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### Step 2: Serve media files in development

**File:** Main `urls.py`

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your patterns ...
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Step 3: Download existing S3 files (Optional)

Create script to download all files from S3:

```python
# download_s3_files.py
import os
import requests
from student_management.models import EBook

bucket = 'writixaidbasebackuspaces'
region = 'ap-southeast-1'
local_media_root = 'media/ebooks/'

os.makedirs(local_media_root, exist_ok=True)

for ebook in EBook.objects.all():
    if ebook.file:
        file_path = ebook.file.name
        file_path = file_path.replace(f'{bucket}/{bucket}/', '')
        file_path = file_path.replace(f'{bucket}/', '')

        s3_url = f'https://{bucket}.s3.{region}.amazonaws.com/{file_path}'

        # Download file
        response = requests.get(s3_url)
        if response.status_code == 200:
            filename = os.path.basename(file_path)
            local_path = os.path.join(local_media_root, filename)

            with open(local_path, 'wb') as f:
                f.write(response.content)

            # Update database
            ebook.file.name = f'ebooks/{filename}'
            ebook.save()

            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download: {file_path}")

print("All files downloaded!")
```

**Pros:**
- ✅ No S3 dependency
- ✅ No AWS credentials needed
- ✅ Simpler deployment
- ✅ Faster access

**Cons:**
- ⚠️ Uses server disk space
- ⚠️ Need to backup files yourself
- ⚠️ Not scalable for large files

---

## Option 4: Use CloudFront CDN (If Available)

If you have CloudFront set up for your S3 bucket:

### Just update URLs:

```python
# In settings.py
CLOUDFRONT_DOMAIN = 'your-distribution.cloudfront.net'

# In template
<a href="https://{{ CLOUDFRONT_DOMAIN }}/{{ ebook.file.name }}">
    📖 Read
</a>
```

**Pros:**
- ✅ No credentials needed
- ✅ Fast CDN delivery
- ✅ Cached globally

**Cons:**
- ⚠️ Requires CloudFront setup
- ⚠️ Additional AWS service

---

## Recommended Solution: Option 1 + Fix Duplicate Paths

**Quickest and easiest:**

1. **Make S3 bucket public** (5 minutes)
   - Update bucket policy
   - Unblock public access

2. **Fix duplicate paths** (2 minutes)
   ```bash
   python manage.py shell < fix_ebook_s3_paths.py
   ```

3. **Test** - Should work immediately!

**No Django changes needed!**
**No AWS credentials in code!**
**No additional packages!**

---

## Summary Comparison

| Solution | Complexity | Speed | Security | Setup Time |
|----------|-----------|-------|----------|------------|
| **Option 1: Public S3** | ⭐ Easy | ⭐⭐⭐ Fast | ⚠️ Public | 5 min |
| **Option 2: Proxy View** | ⭐⭐ Medium | ⭐⭐ Slower | ✅ Login | 10 min |
| **Option 3: Local Storage** | ⭐⭐ Medium | ⭐⭐⭐ Fast | ✅ Secure | 15 min |
| **Option 4: CloudFront** | ⭐⭐⭐ Hard | ⭐⭐⭐ Fastest | ⚠️ Public | 30 min |

**My Recommendation:** Use **Option 1** (Public S3) if files can be public, or **Option 2** (Proxy View) if you need login protection.

Both avoid AWS credentials in your code!
