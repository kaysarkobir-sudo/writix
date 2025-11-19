"""
AWS S3 Settings for Django
Add these to your settings.py file

Location: /Users/macbookpro/Desktop/techgenius/writixaisite/settings.py
"""

# ============================================================================
# AWS S3 CONFIGURATION
# ============================================================================

# AWS Credentials (Get from AWS Console → IAM → Users → Security Credentials)
AWS_ACCESS_KEY_ID = 'YOUR_ACCESS_KEY_HERE'  # Replace with your actual key
AWS_SECRET_ACCESS_KEY = 'YOUR_SECRET_KEY_HERE'  # Replace with your actual secret

# S3 Bucket Configuration
AWS_STORAGE_BUCKET_NAME = 'writixaidbasebackuspaces'  # Your bucket name
AWS_S3_REGION_NAME = 'ap-southeast-1'  # Your bucket region (check in S3 console)
AWS_S3_SIGNATURE_VERSION = 's3v4'  # Required for newer AWS regions

# S3 Settings
AWS_S3_FILE_OVERWRITE = False  # Don't overwrite files with same name
AWS_DEFAULT_ACL = None  # Use bucket's default ACL
AWS_S3_VERIFY = True  # Verify SSL certificates
AWS_QUERYSTRING_AUTH = True  # Use signed URLs (more secure)

# S3 URL Configuration
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'

# Cache Control Headers
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # Cache for 1 day
}

# Media Files (uploads like e-books, images, etc.)
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
MEDIA_ROOT = ''  # Not used with S3

# Use S3 for media file storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# ============================================================================
# ALTERNATIVE: Using Environment Variables (RECOMMENDED for production)
# ============================================================================

"""
# Install python-decouple first: pip install python-decouple

from decouple import config

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='writixaidbasebackuspaces')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='ap-southeast-1')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_QUERYSTRING_AUTH = True

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
MEDIA_ROOT = ''
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Then create .env file in project root:
# AWS_ACCESS_KEY_ID=your_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_here
# AWS_STORAGE_BUCKET_NAME=writixaidbasebackuspaces
# AWS_S3_REGION_NAME=ap-southeast-1
"""

# ============================================================================
# REQUIRED PACKAGES
# ============================================================================

"""
Install these packages:

pip install django-storages
pip install boto3

Then add to INSTALLED_APPS in settings.py:

INSTALLED_APPS = [
    # ... other apps ...
    'storages',
]
"""

# ============================================================================
# TESTING YOUR CONFIGURATION
# ============================================================================

"""
Test in Django shell:

python manage.py shell

>>> from django.core.files.storage import default_storage
>>> from django.core.files.base import ContentFile
>>>
>>> # Test write
>>> path = default_storage.save('test.txt', ContentFile(b'Hello S3!'))
>>> print(f"File saved to: {path}")
>>>
>>> # Test read
>>> file = default_storage.open('test.txt')
>>> print(file.read())
>>>
>>> # Test URL
>>> url = default_storage.url('test.txt')
>>> print(f"URL: {url}")
>>>
>>> # Clean up
>>> default_storage.delete('test.txt')
"""

# ============================================================================
# COMMON REGIONS
# ============================================================================

"""
Replace AWS_S3_REGION_NAME with your bucket's region:

- US East (N. Virginia): us-east-1
- US East (Ohio): us-east-2
- US West (N. California): us-west-1
- US West (Oregon): us-west-2
- Asia Pacific (Mumbai): ap-south-1
- Asia Pacific (Singapore): ap-southeast-1
- Asia Pacific (Sydney): ap-southeast-2
- Asia Pacific (Tokyo): ap-northeast-1
- Europe (Ireland): eu-west-1
- Europe (London): eu-west-2
- Europe (Frankfurt): eu-central-1

Check your bucket region in AWS S3 Console → Select Bucket → Properties → Region
"""
