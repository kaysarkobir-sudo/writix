"""
Comprehensive script to ensure Student table has ALL required columns
Run this with: python manage.py shell < ensure_student_table_complete.py
"""

from django.db import connection

def ensure_student_table_complete():
    """
    Ensure student_management_student table has all required columns
    matching the Student model definition
    """

    # Define ALL columns that should exist in the student table
    all_columns = [
        # Foreign Keys
        ('profile_id', 'BIGINT', 'NOT NULL REFERENCES student_management_profile(id) ON DELETE CASCADE'),
        ('institution_id', 'BIGINT', 'NULL REFERENCES student_management_institution(id) ON DELETE SET NULL'),
        ('student_type_id', 'BIGINT', 'NULL REFERENCES student_management_studenttype(id) ON DELETE SET NULL'),
        ('student_class_id', 'BIGINT', 'NULL REFERENCES student_management_academicclass(id) ON DELETE SET NULL'),
        ('student_section_id', 'BIGINT', 'NULL REFERENCES student_management_section(id) ON DELETE SET NULL'),
        ('previous_student_class_id', 'BIGINT', 'NULL REFERENCES student_management_academicclass(id) ON DELETE SET NULL'),

        # Basic Information
        ('surname', 'VARCHAR(200)', 'NOT NULL'),
        ('first_name', 'VARCHAR(200)', 'NOT NULL'),
        ('last_name', 'VARCHAR(200)', 'NOT NULL'),
        ('other_name', 'VARCHAR(200)', 'DEFAULT \'\''),
        ('gender', 'VARCHAR(10)', 'DEFAULT \'male\''),
        ('religion', 'VARCHAR(50)', 'NULL'),
        ('date_of_birth', 'DATE', 'NULL'),

        # Academic Information
        ('roll_number', 'VARCHAR(20)', 'UNIQUE NOT NULL'),
        ('registration_number', 'VARCHAR(200)', 'UNIQUE NOT NULL'),
        ('batch', 'VARCHAR(50)', 'DEFAULT \'\''),
        ('date_of_admission', 'DATE', 'NULL'),
        ('enrollment_date', 'DATE', 'NULL'),
        ('current_status', 'VARCHAR(10)', 'DEFAULT \'active\''),
        ('discount', 'DECIMAL(5,2)', 'DEFAULT 0'),

        # Father Information
        ('father_name', 'VARCHAR(50)', 'NULL'),
        ('father_mobile', 'VARCHAR(15)', 'NULL'),
        ('father_profession', 'VARCHAR(50)', 'NULL'),
        ('father_photo', 'VARCHAR(100)', 'NULL'),

        # Mother Information
        ('mother_name', 'VARCHAR(50)', 'NULL'),
        ('mother_mobile', 'VARCHAR(15)', 'NULL'),
        ('mother_profession', 'VARCHAR(50)', 'NULL'),
        ('mother_photo', 'VARCHAR(100)', 'NULL'),

        # Guardian Information
        ('guardian', 'VARCHAR(50)', 'NULL'),
        ('relation_with_guardian', 'VARCHAR(50)', 'NULL'),
        ('guardian_username', 'VARCHAR(50)', 'NULL'),
        ('guardian_password', 'VARCHAR(50)', 'NULL'),
        ('parent_first_name', 'VARCHAR(50)', 'NULL'),
        ('parent_last_name', 'VARCHAR(50)', 'NULL'),
        ('parent_mobile', 'VARCHAR(15)', 'NULL'),
        ('parent_email', 'VARCHAR(254)', 'NULL'),

        # Previous School
        ('previous_school_name', 'VARCHAR(200)', 'NULL'),
        ('transfer_certificate', 'VARCHAR(100)', 'NULL'),

        # Other Information
        ('student_username', 'VARCHAR(50)', 'NULL'),
        ('student_password', 'VARCHAR(50)', 'NULL'),
        ('student_email', 'VARCHAR(254)', 'NULL'),
        ('student_mobile_number', 'VARCHAR(15)', 'NULL'),
        ('student_blood_grp', 'VARCHAR(20)', 'NULL'),
        ('birthcert_number', 'VARCHAR(200)', 'UNIQUE NOT NULL'),
        ('national_id', 'VARCHAR(200)', 'UNIQUE NOT NULL'),
        ('student_photo', 'VARCHAR(100)', 'NULL'),
        ('passport', 'VARCHAR(100)', 'NULL'),
        ('present_address', 'TEXT', 'DEFAULT \'\''),
        ('permanent_address', 'TEXT', 'DEFAULT \'\''),
        ('others', 'TEXT', 'DEFAULT \'\''),
        ('firstname', 'TEXT', 'DEFAULT \'\''),
    ]

    with connection.cursor() as cursor:
        db_vendor = connection.vendor
        print(f"Database: {db_vendor}")
        print(f"{'='*70}")
        print("Ensuring Student table has all required columns")
        print(f"{'='*70}\n")

        # Get existing columns
        if db_vendor == 'postgresql':
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='student_management_student'
                ORDER BY ordinal_position;
            """)
        elif db_vendor == 'mysql':
            cursor.execute("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME='student_management_student'
                ORDER BY ORDINAL_POSITION;
            """)
        elif db_vendor == 'sqlite':
            cursor.execute("PRAGMA table_info(student_management_student);")

        existing_columns = set()
        if db_vendor in ['postgresql', 'mysql']:
            existing_columns = {row[0] for row in cursor.fetchall()}
        elif db_vendor == 'sqlite':
            existing_columns = {row[1] for row in cursor.fetchall()}

        existing_columns.add('id')  # ID always exists

        print(f"Found {len(existing_columns)} existing columns")
        print(f"Model defines {len(all_columns)} columns\n")

        added_count = 0
        skipped_count = 0
        error_count = 0

        for col_name, col_type, col_constraint in all_columns:
            if col_name in existing_columns:
                print(f"✓ {col_name:35} - Already exists")
                skipped_count += 1
                continue

            print(f"➕ {col_name:35} - Adding...", end=' ')

            try:
                if db_vendor == 'postgresql':
                    # PostgreSQL - handle constraints carefully
                    if 'REFERENCES' in col_constraint:
                        # Foreign key - add column first, then constraint
                        parts = col_constraint.split('REFERENCES')
                        base_constraint = parts[0].strip()
                        fk_constraint = 'REFERENCES' + parts[1]

                        cursor.execute(f"""
                            ALTER TABLE student_management_student
                            ADD COLUMN {col_name} {col_type} {base_constraint};
                        """)

                        # Add FK constraint separately
                        constraint_name = f"student_management_student_{col_name}_fk"
                        cursor.execute(f"""
                            ALTER TABLE student_management_student
                            DROP CONSTRAINT IF EXISTS {constraint_name};
                        """)
                        cursor.execute(f"""
                            ALTER TABLE student_management_student
                            ADD CONSTRAINT {constraint_name}
                            FOREIGN KEY ({col_name})
                            {fk_constraint};
                        """)
                    else:
                        # Regular column
                        cursor.execute(f"""
                            ALTER TABLE student_management_student
                            ADD COLUMN {col_name} {col_type} {col_constraint};
                        """)

                elif db_vendor == 'mysql':
                    cursor.execute(f"""
                        ALTER TABLE student_management_student
                        ADD COLUMN {col_name} {col_type} {col_constraint};
                    """)

                elif db_vendor == 'sqlite':
                    # SQLite - simpler syntax
                    sqlite_type = col_type.replace('VARCHAR', 'TEXT')
                    cursor.execute(f"""
                        ALTER TABLE student_management_student
                        ADD COLUMN {col_name} {sqlite_type} {col_constraint};
                    """)

                print("✓")
                added_count += 1

            except Exception as e:
                print(f"✗ Error: {str(e)[:50]}")
                error_count += 1

        # Create indexes for foreign keys
        print(f"\n{'='*70}")
        print("Creating indexes for foreign keys...")
        print(f"{'='*70}\n")

        fk_columns = [
            'profile_id', 'institution_id', 'student_type_id',
            'student_class_id', 'student_section_id', 'previous_student_class_id'
        ]

        for col_name in fk_columns:
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS idx_{col_name}
                        ON student_management_student({col_name});
                    """)
                    print(f"✓ Index created: idx_{col_name}")
                except Exception as e:
                    print(f"✗ Index failed for {col_name}: {str(e)[:50]}")

        print(f"\n{'='*70}")
        print("Summary:")
        print(f"{'='*70}")
        print(f"✓ Columns already existed: {skipped_count}")
        print(f"➕ Columns added:          {added_count}")
        print(f"✗ Errors:                 {error_count}")
        print(f"{'='*70}\n")

        if added_count > 0:
            print("✓ Student table updated successfully!")
            print("Your Student model should now work without errors.")
        elif error_count > 0:
            print("⚠ Some errors occurred. Try Django migrations:")
            print("  python manage.py makemigrations student_management")
            print("  python manage.py migrate student_management")
        else:
            print("✓ Student table already has all required columns!")

# Run the fix
if __name__ == '__main__':
    ensure_student_table_complete()
else:
    ensure_student_table_complete()
