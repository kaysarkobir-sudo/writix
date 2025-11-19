# Fix AWS S3 SignatureDoesNotMatch Error for E-Books

## The Problem

Error when accessing e-book files:
```xml
<Code>SignatureDoesNotMatch</Code>
<Message>The request signature we calculated does not match the signature you provided.</Message>
<Resource>writixaidbasebackuspaces/writixaidbasebackuspaces/ebooks/Lecturesheet.png</Resource>
```

**Issues identified:**
1. Duplicate bucket name in path (`writixaidbasebackuspaces` appears twice)
2. AWS signature not matching (credentials or configuration issue)
3. Possible CORS or permission issues

---

## Solution 1: Fix Django Settings (Most Common) ⚡

### Step 1: Check your `settings.py`

**File:** `/Users/macbookpro/Desktop/techgenius/writixaisite/settings.py`

Add or update these AWS S3 settings:

```python
# AWS S3 Configuration
AWS_ACCESS_KEY_ID = 'your-access-key-id'  # Get from AWS Console
AWS_SECRET_ACCESS_KEY = 'your-secret-access-key'  # Get from AWS Console
AWS_STORAGE_BUCKET_NAME = 'writixaidbasebackuspaces'  # Your bucket name
AWS_S3_REGION_NAME = 'ap-southeast-1'  # Your bucket region (e.g., us-east-1, ap-south-1)
AWS_S3_SIGNATURE_VERSION = 's3v4'  # Required for newer regions
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None  # Or 'public-read' if files should be public
AWS_S3_VERIFY = True

# S3 URL Configuration
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Static and Media Files
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = 'media/'

# Use S3 for media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### Step 2: Install required package

```bash
pip install django-storages boto3
```

### Step 3: Add to INSTALLED_APPS

In `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'storages',
]
```

---

## Solution 2: Fix Duplicate Bucket Name in File Paths

The error shows duplicated bucket name in path. This needs to be fixed in the database.

### Create a cleanup script:

**File:** `fix_ebook_s3_paths.py`

```python
"""
Fix duplicate bucket name in EBook file paths
Run with: python manage.py shell < fix_ebook_s3_paths.py
"""

from student_management.models import EBook

def fix_ebook_paths():
    """Remove duplicate bucket name from file paths"""

    print("="*70)
    print("Fixing EBook S3 file paths...")
    print("="*70)

    ebooks = EBook.objects.all()
    fixed_count = 0

    for ebook in ebooks:
        old_path = ebook.file.name

        # Check if path has duplicate bucket name
        if 'writixaidbasebackuspaces/writixaidbasebackuspaces/' in old_path:
            # Remove the duplicate
            new_path = old_path.replace(
                'writixaidbasebackuspaces/writixaidbasebackuspaces/',
                'writixaidbasebackuspaces/'
            )

            print(f"\nFixing: {ebook.title}")
            print(f"  OLD: {old_path}")
            print(f"  NEW: {new_path}")

            # Update the file path
            ebook.file.name = new_path
            ebook.save()
            fixed_count += 1

        # Also fix cover_image if it exists
        if hasattr(ebook, 'cover_image') and ebook.cover_image:
            old_cover_path = ebook.cover_image.name
            if 'writixaidbasebackuspaces/writixaidbasebackuspaces/' in old_cover_path:
                new_cover_path = old_cover_path.replace(
                    'writixaidbasebackuspaces/writixaidbasebackuspaces/',
                    'writixaidbasebackuspaces/'
                )
                ebook.cover_image.name = new_cover_path
                ebook.save()

    print(f"\n{'='*70}")
    print(f"✓ Fixed {fixed_count} e-book file paths")
    print(f"{'='*70}")

# Run the fix
if __name__ == '__main__':
    fix_ebook_paths()
else:
    fix_ebook_paths()
```

Run it:
```bash
cd /Users/macbookpro/Desktop/techgenius/writixaisite
python manage.py shell < fix_ebook_s3_paths.py
```

---

## Solution 3: Make Files Public (If Appropriate)

If e-books should be publicly accessible:

### Option A: Update S3 Bucket Policy

Go to AWS S3 Console → Your Bucket → Permissions → Bucket Policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::writixaidbasebackuspaces/ebooks/*"
        }
    ]
}
```

### Option B: Use Signed URLs with Longer Expiry

In your view, generate signed URLs:

```python
from django.core.files.storage import default_storage
from datetime import timedelta

@login_required
def ebook_list(request):
    ebooks = EBook.objects.all().order_by('-id')

    # Generate signed URLs for each ebook
    for ebook in ebooks:
        if ebook.file:
            # Generate URL that expires in 1 hour
            ebook.signed_url = default_storage.url(
                ebook.file.name,
                expire=3600  # 1 hour in seconds
            )

    context = {'ebooks': ebooks}
    return render(request, 'student_management/library/ebook_list.html', context)
```

Then in template, use:
```html
<a href="{{ ebook.signed_url }}" target="_blank">📖 Read</a>
```

---

## Solution 4: Check AWS IAM Permissions

Make sure your AWS IAM user has these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::writixaidbasebackuspaces/*",
                "arn:aws:s3:::writixaidbasebackuspaces"
            ]
        }
    ]
}
```

---

## Solution 5: Configure CORS (If accessing from browser)

In AWS S3 Console → Your Bucket → Permissions → CORS:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3000
    }
]
```

---

## Quick Diagnostic Steps

### 1. Check current settings

In Django shell:
```python
python manage.py shell

from django.conf import settings
print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"Region: {settings.AWS_S3_REGION_NAME}")
print(f"Access Key: {settings.AWS_ACCESS_KEY_ID[:5]}...")  # Show first 5 chars
```

### 2. Test S3 connection

```python
import boto3
from django.conf import settings

s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

# List buckets
buckets = s3.list_buckets()
print("Available buckets:", [b['Name'] for b in buckets['Buckets']])
```

### 3. Check file paths in database

```python
from student_management.models import EBook

for ebook in EBook.objects.all()[:5]:
    print(f"{ebook.title}: {ebook.file.name}")
```

---

## Common Issues & Fixes

### Issue 1: "Access Denied"
**Fix:** Check IAM permissions (Solution 4)

### Issue 2: "NoSuchKey"
**Fix:** File path is wrong - use Solution 2 to fix paths

### Issue 3: "SignatureDoesNotMatch"
**Fix:**
1. Check AWS credentials in settings.py
2. Verify signature version is 's3v4'
3. Check region matches your bucket

### Issue 4: Files not accessible
**Fix:**
1. Make files public (Solution 3A)
2. Or use signed URLs (Solution 3B)

---

## Recommended Fix Order

1. ✅ **First:** Fix Django settings (Solution 1)
2. ✅ **Second:** Fix duplicate paths (Solution 2)
3. ✅ **Third:** Configure CORS (Solution 5)
4. ✅ **Fourth:** Test with signed URLs (Solution 3B)
5. ✅ **Last:** Make public if needed (Solution 3A)

---

## Environment Variables (Recommended)

Instead of hardcoding credentials in settings.py, use environment variables:

**In `settings.py`:**
```python
import os
from decouple import config  # pip install python-decouple

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='writixaidbasebackuspaces')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='ap-southeast-1')
```

**Create `.env` file:**
```env
AWS_ACCESS_KEY_ID=your-actual-key-here
AWS_SECRET_ACCESS_KEY=your-actual-secret-here
AWS_STORAGE_BUCKET_NAME=writixaidbasebackuspaces
AWS_S3_REGION_NAME=ap-southeast-1
```

**Add to `.gitignore`:**
```
.env
```

---

## Testing After Fix

1. Restart Django server
2. Navigate to: `http://127.0.0.1:8000/student-management/library/ebooks/`
3. Click "Read" on an e-book
4. Should open the PDF/file without error

---

## Need AWS Credentials?

If you don't have AWS credentials:

1. Go to AWS Console → IAM → Users
2. Create new user or select existing
3. Attach policy: `AmazonS3FullAccess` or custom policy
4. Generate access keys
5. Copy Access Key ID and Secret Access Key
6. Add to settings.py or .env file

---

## Summary

**Most Likely Fix:**
1. Add correct AWS settings to settings.py
2. Fix duplicate bucket name in file paths
3. Restart server

**Test:** Click "Read" on an e-book - should work!
