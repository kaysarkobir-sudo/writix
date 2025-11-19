"""
Django shell script to add missing student_type_id column to Student table
Run this with: python manage.py shell < fix_student_type_column.py
"""

from django.db import connection

def add_student_type_column():
    """Add student_type_id column to student_management_student table"""

    with connection.cursor() as cursor:
        # Get database vendor
        db_vendor = connection.vendor

        print(f"Database: {db_vendor}")
        print("Adding student_type_id column to student_management_student table...")

        try:
            if db_vendor == 'postgresql':
                # PostgreSQL syntax
                cursor.execute("""
                    ALTER TABLE student_management_student
                    ADD COLUMN IF NOT EXISTS student_type_id BIGINT NULL;
                """)

                # Add foreign key constraint
                cursor.execute("""
                    ALTER TABLE student_management_student
                    DROP CONSTRAINT IF EXISTS student_management_student_type_id_fk;
                """)

                cursor.execute("""
                    ALTER TABLE student_management_student
                    ADD CONSTRAINT student_management_student_type_id_fk
                    FOREIGN KEY (student_type_id)
                    REFERENCES student_management_studenttype(id)
                    ON DELETE SET NULL;
                """)

                print("✓ PostgreSQL: student_type_id column added successfully")

            elif db_vendor == 'mysql':
                # MySQL syntax
                cursor.execute("""
                    ALTER TABLE student_management_student
                    ADD COLUMN student_type_id BIGINT NULL;
                """)

                cursor.execute("""
                    ALTER TABLE student_management_student
                    ADD CONSTRAINT student_management_student_type_id_fk
                    FOREIGN KEY (student_type_id)
                    REFERENCES student_management_studenttype(id)
                    ON DELETE SET NULL;
                """)

                print("✓ MySQL: student_type_id column added successfully")

            elif db_vendor == 'sqlite':
                # SQLite doesn't support ALTER COLUMN with constraints easily
                # We need to check if column exists first
                cursor.execute("PRAGMA table_info(student_management_student);")
                columns = [row[1] for row in cursor.fetchall()]

                if 'student_type_id' not in columns:
                    cursor.execute("""
                        ALTER TABLE student_management_student
                        ADD COLUMN student_type_id INTEGER NULL
                        REFERENCES student_management_studenttype(id)
                        ON DELETE SET NULL;
                    """)
                    print("✓ SQLite: student_type_id column added successfully")
                else:
                    print("✓ SQLite: student_type_id column already exists")
            else:
                print(f"✗ Unsupported database: {db_vendor}")
                return False

            # Create index for better query performance
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_student_type_id
                    ON student_management_student(student_type_id);
                """)
                print("✓ Index created for student_type_id")
            except Exception as e:
                print(f"Note: Index creation skipped: {e}")

            print("\n✓ Successfully added student_type_id column!")
            print("You can now use Student.student_type in queries.")
            return True

        except Exception as e:
            print(f"\n✗ Error adding column: {e}")
            print("\nAlternative: Run Django migrations:")
            print("  python manage.py makemigrations student_management")
            print("  python manage.py migrate student_management")
            return False

# Run the fix
if __name__ == '__main__':
    add_student_type_column()
else:
    # When run via shell
    add_student_type_column()
