"""
Comprehensive fix script to add ALL missing foreign key columns to Student table
Run this with: python manage.py shell < fix_all_student_columns.py
"""

from django.db import connection

def add_all_missing_columns():
    """Add all missing foreign key columns to student_management_student table"""

    # Define all foreign key columns that should exist
    columns_to_add = [
        {
            'name': 'institution_id',
            'type': 'BIGINT',
            'reference_table': 'student_management_institution',
            'description': 'Institution/School'
        },
        {
            'name': 'student_type_id',
            'type': 'BIGINT',
            'reference_table': 'student_management_studenttype',
            'description': 'Student Type'
        },
        {
            'name': 'student_class_id',
            'type': 'BIGINT',
            'reference_table': 'student_management_academicclass',
            'description': 'Academic Class'
        },
        {
            'name': 'student_section_id',
            'type': 'BIGINT',
            'reference_table': 'student_management_section',
            'description': 'Section'
        },
        {
            'name': 'previous_student_class_id',
            'type': 'BIGINT',
            'reference_table': 'student_management_academicclass',
            'description': 'Previous Academic Class'
        },
        {
            'name': 'profile_id',
            'type': 'BIGINT',
            'reference_table': 'student_management_profile',
            'description': 'User Profile'
        }
    ]

    with connection.cursor() as cursor:
        db_vendor = connection.vendor
        print(f"Database: {db_vendor}")
        print(f"{'='*60}")
        print("Adding missing foreign key columns to student_management_student")
        print(f"{'='*60}\n")

        added_count = 0
        skipped_count = 0
        error_count = 0

        for col in columns_to_add:
            column_name = col['name']
            column_type = col['type']
            ref_table = col['reference_table']
            description = col['description']

            print(f"Processing: {column_name} ({description})...")

            try:
                if db_vendor == 'postgresql':
                    # Check if column exists
                    cursor.execute("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name='student_management_student'
                        AND column_name=%s;
                    """, [column_name])

                    if cursor.fetchone():
                        print(f"  ✓ Already exists - skipping")
                        skipped_count += 1
                        continue

                    # Add column
                    cursor.execute(f"""
                        ALTER TABLE student_management_student
                        ADD COLUMN {column_name} {column_type} NULL;
                    """)

                    # Add foreign key constraint
                    constraint_name = f"student_management_student_{column_name}_fk"
                    cursor.execute(f"""
                        ALTER TABLE student_management_student
                        DROP CONSTRAINT IF EXISTS {constraint_name};
                    """)

                    cursor.execute(f"""
                        ALTER TABLE student_management_student
                        ADD CONSTRAINT {constraint_name}
                        FOREIGN KEY ({column_name})
                        REFERENCES {ref_table}(id)
                        ON DELETE SET NULL;
                    """)

                    # Add index
                    index_name = f"idx_{column_name}"
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS {index_name}
                        ON student_management_student({column_name});
                    """)

                    print(f"  ✓ Added successfully")
                    added_count += 1

                elif db_vendor == 'mysql':
                    # Check if column exists
                    cursor.execute("""
                        SELECT COLUMN_NAME
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME='student_management_student'
                        AND COLUMN_NAME=%s;
                    """, [column_name])

                    if cursor.fetchone():
                        print(f"  ✓ Already exists - skipping")
                        skipped_count += 1
                        continue

                    # Add column with foreign key
                    cursor.execute(f"""
                        ALTER TABLE student_management_student
                        ADD COLUMN {column_name} {column_type} NULL,
                        ADD CONSTRAINT student_management_student_{column_name}_fk
                        FOREIGN KEY ({column_name})
                        REFERENCES {ref_table}(id)
                        ON DELETE SET NULL;
                    """)

                    # Add index
                    cursor.execute(f"""
                        CREATE INDEX idx_{column_name}
                        ON student_management_student({column_name});
                    """)

                    print(f"  ✓ Added successfully")
                    added_count += 1

                elif db_vendor == 'sqlite':
                    # Check if column exists
                    cursor.execute("PRAGMA table_info(student_management_student);")
                    existing_columns = [row[1] for row in cursor.fetchall()]

                    if column_name in existing_columns:
                        print(f"  ✓ Already exists - skipping")
                        skipped_count += 1
                        continue

                    # Add column
                    cursor.execute(f"""
                        ALTER TABLE student_management_student
                        ADD COLUMN {column_name} INTEGER NULL
                        REFERENCES {ref_table}(id)
                        ON DELETE SET NULL;
                    """)

                    print(f"  ✓ Added successfully")
                    added_count += 1

            except Exception as e:
                print(f"  ✗ Error: {e}")
                error_count += 1
                continue

        print(f"\n{'='*60}")
        print("Summary:")
        print(f"  ✓ Added:   {added_count} columns")
        print(f"  - Skipped: {skipped_count} columns (already exist)")
        print(f"  ✗ Errors:  {error_count} columns")
        print(f"{'='*60}")

        if added_count > 0:
            print("\n✓ Successfully updated student table!")
            print("Your Student model should now work correctly.")
        elif skipped_count > 0 and error_count == 0:
            print("\n✓ All columns already exist!")
        else:
            print("\n⚠ Some errors occurred. Try running Django migrations:")
            print("  python manage.py makemigrations student_management")
            print("  python manage.py migrate student_management")

# Run the fix
if __name__ == '__main__':
    add_all_missing_columns()
else:
    # When run via shell
    add_all_missing_columns()
