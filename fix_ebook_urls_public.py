"""
Fix EBook URLs for Public S3 Access (No AWS Credentials Needed)
Run with: python manage.py shell < fix_ebook_urls_public.py

This script:
1. Removes duplicate bucket names from file paths
2. Creates direct S3 URLs that work when bucket is public
3. No AWS credentials required
"""

from student_management.models import EBook

def fix_ebook_urls_for_public_access():
    """Fix e-book file paths to use direct S3 URLs"""

    # Your S3 bucket configuration
    bucket_name = 'writixaidbasebackuspaces'
    region = 'ap-southeast-1'  # Change to your actual region

    print("="*70)
    print("Fixing E-Book URLs for Public S3 Access")
    print("="*70)
    print(f"Bucket: {bucket_name}")
    print(f"Region: {region}")
    print(f"Direct URL format: https://{bucket_name}.s3.{region}.amazonaws.com/...\n")

    try:
        ebooks = EBook.objects.all()
        total = ebooks.count()
        fixed = 0

        print(f"Total e-books to process: {total}\n")

        for ebook in ebooks:
            if ebook.file:
                old_path = ebook.file.name

                # Remove duplicate bucket name
                new_path = old_path
                new_path = new_path.replace(f'{bucket_name}/{bucket_name}/', '')
                new_path = new_path.replace(f'{bucket_name}/', '')

                # Create direct S3 URL for reference
                direct_url = f'https://{bucket_name}.s3.{region}.amazonaws.com/{new_path}'

                if old_path != new_path:
                    print(f"Fixing: {ebook.title}")
                    print(f"  OLD: {old_path}")
                    print(f"  NEW: {new_path}")
                    print(f"  URL: {direct_url}")

                    # Update database
                    ebook.file.name = new_path
                    ebook.save()
                    fixed += 1
                else:
                    print(f"OK: {ebook.title}")
                    print(f"  Path: {new_path}")
                    print(f"  URL: {direct_url}")

                print()  # Blank line

        print("="*70)
        print("SUMMARY:")
        print(f"  Total processed: {total}")
        print(f"  Fixed: {fixed}")
        print(f"  Already correct: {total - fixed}")
        print("="*70)

        if fixed > 0:
            print("\n✓ E-book paths have been fixed!")
        else:
            print("\n✓ All paths were already correct!")

        print("\nNext steps:")
        print("  1. Make sure your S3 bucket is public")
        print("  2. Restart Django server")
        print("  3. Test by clicking 'Read' on an e-book")
        print("\nFiles will be accessible at:")
        print(f"  https://{bucket_name}.s3.{region}.amazonaws.com/[filepath]")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

# Run the fix
if __name__ == '__main__':
    fix_ebook_urls_for_public_access()
else:
    fix_ebook_urls_for_public_access()
