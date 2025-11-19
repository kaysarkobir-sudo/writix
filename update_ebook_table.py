"""
Update EBook Table - Add Missing Columns
Run this with: python manage.py shell < update_ebook_table.py

This script adds all missing columns to the existing EBook table
"""

from django.db import connection

def update_ebook_table():
    """Add missing columns to EBook table"""

    with connection.cursor() as cursor:
        db_vendor = connection.vendor
        print(f"Database: {db_vendor}")
        print(f"{'='*70}")
        print("Updating EBook table with missing columns...")
        print(f"{'='*70}\n")

        try:
            # Check current table structure
            print("Checking current EBook table structure...")

            if db_vendor == 'postgresql':
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'student_management_ebook'
                    ORDER BY ordinal_position;
                """)
            elif db_vendor == 'mysql':
                cursor.execute("""
                    SHOW COLUMNS FROM student_management_ebook;
                """)
            elif db_vendor == 'sqlite':
                cursor.execute("""
                    PRAGMA table_info(student_management_ebook);
                """)

            existing_columns = [row[0] if db_vendor == 'postgresql' else (row[0] if db_vendor == 'mysql' else row[1]) for row in cursor.fetchall()]
            print(f"Current columns: {', '.join(existing_columns)}\n")

            # Define columns to add
            columns_to_add = {
                'author': "VARCHAR(200) DEFAULT ''",
                'cover_image': "VARCHAR(100) NULL",
                'category': "VARCHAR(50) DEFAULT ''",
                'format': "VARCHAR(10) DEFAULT 'pdf'",
                'file_size': "VARCHAR(50) DEFAULT ''",
                'pages': "INTEGER NULL",
                'is_public': "BOOLEAN DEFAULT TRUE" if db_vendor != 'mysql' else "BOOLEAN DEFAULT 1",
                'download_count': "INTEGER DEFAULT 0",
                'view_count': "INTEGER DEFAULT 0",
                'uploaded_on': "DATE DEFAULT CURRENT_DATE" if db_vendor != 'mysql' else "DATE DEFAULT (CURRENT_DATE)",
                'uploaded_by_id': "INTEGER NULL"
            }

            # Add missing columns
            for column_name, column_def in columns_to_add.items():
                if column_name not in existing_columns:
                    try:
                        print(f"Adding column: {column_name}...")

                        if db_vendor == 'postgresql':
                            cursor.execute(f"""
                                ALTER TABLE student_management_ebook
                                ADD COLUMN {column_name} {column_def};
                            """)
                        elif db_vendor == 'mysql':
                            cursor.execute(f"""
                                ALTER TABLE student_management_ebook
                                ADD COLUMN {column_name} {column_def};
                            """)
                        elif db_vendor == 'sqlite':
                            cursor.execute(f"""
                                ALTER TABLE student_management_ebook
                                ADD COLUMN {column_name} {column_def};
                            """)

                        print(f"  ✓ Column '{column_name}' added successfully")
                    except Exception as e:
                        print(f"  ✗ Error adding column '{column_name}': {e}")
                else:
                    print(f"  ✓ Column '{column_name}' already exists")

            # Add foreign key constraint for uploaded_by_id (if supported)
            if 'uploaded_by_id' not in existing_columns:
                try:
                    if db_vendor == 'postgresql':
                        print("\nAdding foreign key constraint...")
                        cursor.execute("""
                            ALTER TABLE student_management_ebook
                            ADD CONSTRAINT fk_ebook_uploaded_by
                            FOREIGN KEY (uploaded_by_id) REFERENCES auth_user(id)
                            ON DELETE SET NULL;
                        """)
                        print("  ✓ Foreign key constraint added")
                    elif db_vendor == 'mysql':
                        print("\nAdding foreign key constraint...")
                        cursor.execute("""
                            ALTER TABLE student_management_ebook
                            ADD CONSTRAINT fk_ebook_uploaded_by
                            FOREIGN KEY (uploaded_by_id) REFERENCES auth_user(id)
                            ON DELETE SET NULL;
                        """)
                        print("  ✓ Foreign key constraint added")
                    # SQLite doesn't support adding foreign keys to existing tables
                except Exception as e:
                    print(f"  ⚠ Could not add foreign key constraint: {e}")
                    print(f"  (This is OK - the column still works without the constraint)")

            # Create indexes
            print("\nCreating indexes...")
            indexes_to_create = [
                ('idx_ebook_category', 'category'),
                ('idx_ebook_format', 'format'),
                ('idx_ebook_is_public', 'is_public'),
                ('idx_ebook_uploaded_on', 'uploaded_on'),
            ]

            for index_name, column in indexes_to_create:
                try:
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS {index_name}
                        ON student_management_ebook({column});
                    """)
                    print(f"  ✓ Index '{index_name}' created")
                except Exception as e:
                    print(f"  ⚠ Could not create index '{index_name}': {e}")

            print("\n" + "="*70)
            print("✓ EBook table updated successfully!")
            print("="*70)
            print("\nAdded columns:")
            print("  - author (VARCHAR 200)")
            print("  - cover_image (VARCHAR 100)")
            print("  - category (VARCHAR 50)")
            print("  - format (VARCHAR 10)")
            print("  - file_size (VARCHAR 50)")
            print("  - pages (INTEGER)")
            print("  - is_public (BOOLEAN)")
            print("  - download_count (INTEGER)")
            print("  - view_count (INTEGER)")
            print("  - uploaded_on (DATE)")
            print("  - uploaded_by_id (INTEGER)")
            print("\nYour EBook system is now ready to use!")
            print("\nNext steps:")
            print("  1. Refresh your browser")
            print("  2. Navigate to: http://127.0.0.1:8000/student-management/library/ebooks/")
            print("  3. Start uploading e-books!")

            return True

        except Exception as e:
            print(f"\n✗ Error updating table: {e}")
            print("\nAlternative: Use Django migrations:")
            print("  1. Add the full EBook model to your models.py")
            print("  2. Run: python manage.py makemigrations student_management")
            print("  3. Run: python manage.py migrate student_management")
            return False

# Run the update
if __name__ == '__main__':
    update_ebook_table()
else:
    update_ebook_table()
