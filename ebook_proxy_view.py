"""
E-Book Proxy View - Serve files from S3 without credentials
Add this function to your student_management/views.py

This view:
1. Fetches files from S3 (no credentials needed if bucket is public)
2. Serves through Django (access control with login)
3. Fixes duplicate bucket names automatically
"""

import requests
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def serve_ebook(request, ebook_id):
    """
    Proxy view to serve e-books from S3 without Django-storages

    Usage:
    1. Add to views.py
    2. Add URL: path('library/ebooks/<int:ebook_id>/view/', views.serve_ebook, name='serve_ebook')
    3. In template: <a href="{% url 'serve_ebook' ebook.id %}">Read</a>
    """

    try:
        # Get the ebook
        ebook = get_object_or_404(EBook, id=ebook_id)

        # S3 Configuration
        bucket = 'writixaidbasebackuspaces'
        region = 'ap-southeast-1'  # Change to your actual region

        # Get file path and clean it
        file_path = ebook.file.name

        # Remove duplicate bucket name if present
        file_path = file_path.replace(f'{bucket}/{bucket}/', '')
        file_path = file_path.replace(f'{bucket}/', '')

        # Build S3 URL
        s3_url = f'https://{bucket}.s3.{region}.amazonaws.com/{file_path}'

        # Fetch file from S3
        print(f"Fetching: {s3_url}")  # For debugging
        response = requests.get(s3_url, stream=True, timeout=30)

        if response.status_code != 200:
            print(f"S3 Error: {response.status_code}")
            raise Http404(f"File not found on S3 (Status: {response.status_code})")

        # Determine content type
        content_type = response.headers.get('Content-Type', 'application/pdf')

        # Determine file extension
        file_extension = file_path.split('.')[-1].lower() if '.' in file_path else 'pdf'

        # Map extensions to content types
        content_types = {
            'pdf': 'application/pdf',
            'epub': 'application/epub+zip',
            'mobi': 'application/x-mobipocket-ebook',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        }

        content_type = content_types.get(file_extension, content_type)

        # Create Django response
        django_response = HttpResponse(response.content, content_type=content_type)

        # Set filename for download
        safe_title = "".join(c for c in ebook.title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_title}.{file_extension}"

        # inline = view in browser, attachment = download
        django_response['Content-Disposition'] = f'inline; filename="{filename}"'

        # Update view count (if field exists)
        try:
            if hasattr(ebook, 'view_count'):
                ebook.view_count += 1
                ebook.save(update_fields=['view_count'])
        except:
            pass  # Ignore if field doesn't exist

        return django_response

    except EBook.DoesNotExist:
        raise Http404("E-book not found in database")

    except requests.RequestException as e:
        print(f"Request error: {e}")
        raise Http404(f"Error fetching file from S3: {str(e)}")

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise Http404(f"Error loading file: {str(e)}")


@login_required
def download_ebook(request, ebook_id):
    """
    Download ebook (forces download instead of viewing in browser)

    URL: path('library/ebooks/<int:ebook_id>/download/', views.download_ebook, name='download_ebook')
    Template: <a href="{% url 'download_ebook' ebook.id %}">Download</a>
    """

    try:
        ebook = get_object_or_404(EBook, id=ebook_id)

        bucket = 'writixaidbasebackuspaces'
        region = 'ap-southeast-1'

        file_path = ebook.file.name
        file_path = file_path.replace(f'{bucket}/{bucket}/', '')
        file_path = file_path.replace(f'{bucket}/', '')

        s3_url = f'https://{bucket}.s3.{region}.amazonaws.com}/{file_path}'

        response = requests.get(s3_url, stream=True, timeout=30)

        if response.status_code != 200:
            raise Http404("File not found")

        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        file_extension = file_path.split('.')[-1].lower() if '.' in file_path else 'pdf'

        django_response = HttpResponse(response.content, content_type=content_type)

        # Force download
        safe_title = "".join(c for c in ebook.title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_title}.{file_extension}"
        django_response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Update download count (if field exists)
        try:
            if hasattr(ebook, 'download_count'):
                ebook.download_count += 1
                ebook.save(update_fields=['download_count'])
        except:
            pass

        return django_response

    except Exception as e:
        raise Http404(f"Error downloading file: {str(e)}")


# ============================================================================
# INSTALLATION INSTRUCTIONS
# ============================================================================

"""
1. Install requests:
   pip install requests

2. Add to student_management/views.py:
   - Copy serve_ebook() function
   - Copy download_ebook() function

3. Add to student_management/urls.py:

   urlpatterns = [
       # ... existing patterns ...

       # E-Book proxy views
       path('library/ebooks/<int:ebook_id>/view/', views.serve_ebook, name='serve_ebook'),
       path('library/ebooks/<int:ebook_id>/download/', views.download_ebook, name='download_ebook'),
   ]

4. Update templates/student_management/library/ebook_list.html:

   Replace:
   <a href="{{ ebook.file.url }}" target="_blank">📖 Read</a>
   <a href="{{ ebook.file.url }}" download>⬇️ Download</a>

   With:
   <a href="{% url 'serve_ebook' ebook.id %}" target="_blank">📖 Read</a>
   <a href="{% url 'download_ebook' ebook.id %}">⬇️ Download</a>

5. Make sure S3 bucket is public (see ALTERNATIVE_S3_SOLUTIONS.md)

6. Test by clicking Read/Download buttons
"""
