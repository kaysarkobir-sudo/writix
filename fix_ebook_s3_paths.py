"""
Fix duplicate bucket name in EBook file paths
Run with: python manage.py shell < fix_ebook_s3_paths.py

This script removes duplicate bucket names from S3 file paths
Example: writixaidbasebackuspaces/writixaidbasebackuspaces/ebooks/file.pdf
     --> writixaidbasebackuspaces/ebooks/file.pdf
"""

from student_management.models import EBook

def fix_ebook_paths():
    """Remove duplicate bucket name from file paths"""

    print("="*70)
    print("Fixing EBook S3 file paths...")
    print("="*70)

    try:
        ebooks = EBook.objects.all()
        total_count = ebooks.count()
        fixed_count = 0
        skipped_count = 0

        print(f"\nTotal e-books to check: {total_count}\n")

        for ebook in ebooks:
            print(f"Checking: {ebook.title}")

            # Fix main file path
            if ebook.file:
                old_path = ebook.file.name
                needs_fix = False

                # Check if path has duplicate bucket name
                if 'writixaidbasebackuspaces/writixaidbasebackuspaces/' in old_path:
                    # Remove the duplicate
                    new_path = old_path.replace(
                        'writixaidbasebackuspaces/writixaidbasebackuspaces/',
                        ''  # Remove completely, keep just the file path
                    )
                    needs_fix = True
                elif old_path.startswith('writixaidbasebackuspaces/'):
                    # Remove bucket name prefix entirely
                    new_path = old_path.replace('writixaidbasebackuspaces/', '', 1)
                    needs_fix = True

                if needs_fix:
                    print(f"  OLD: {old_path}")
                    print(f"  NEW: {new_path}")

                    # Update the file path
                    ebook.file.name = new_path
                    ebook.save()
                    fixed_count += 1
                else:
                    print(f"  ✓ Path OK: {old_path}")
                    skipped_count += 1

            # Also fix cover_image if it exists
            try:
                if hasattr(ebook, 'cover_image') and ebook.cover_image:
                    old_cover_path = ebook.cover_image.name
                    needs_cover_fix = False

                    if 'writixaidbasebackuspaces/writixaidbasebackuspaces/' in old_cover_path:
                        new_cover_path = old_cover_path.replace(
                            'writixaidbasebackuspaces/writixaidbasebackuspaces/',
                            ''
                        )
                        needs_cover_fix = True
                    elif old_cover_path.startswith('writixaidbasebackuspaces/'):
                        new_cover_path = old_cover_path.replace('writixaidbasebackuspaces/', '', 1)
                        needs_cover_fix = True

                    if needs_cover_fix:
                        print(f"  Cover OLD: {old_cover_path}")
                        print(f"  Cover NEW: {new_cover_path}")
                        ebook.cover_image.name = new_cover_path
                        ebook.save()
            except Exception as e:
                print(f"  ⚠ Could not check cover_image: {e}")

            print()  # Blank line between ebooks

        print(f"{'='*70}")
        print(f"SUMMARY:")
        print(f"  Total e-books checked: {total_count}")
        print(f"  Fixed: {fixed_count}")
        print(f"  Already correct: {skipped_count}")
        print(f"{'='*70}")

        if fixed_count > 0:
            print("\n✓ E-book file paths have been fixed!")
            print("  Next steps:")
            print("  1. Restart your Django server")
            print("  2. Clear browser cache")
            print("  3. Test by clicking 'Read' on an e-book")
        else:
            print("\n✓ All e-book paths are already correct!")
            print("  The duplicate bucket name issue is not in the database.")
            print("  Check your AWS S3 settings in settings.py instead.")

        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nIf EBook model doesn't exist, you may need to:")
        print("  1. Create the EBook table first")
        print("  2. Run migrations")
        return False

# Run the fix
if __name__ == '__main__':
    fix_ebook_paths()
else:
    fix_ebook_paths()
