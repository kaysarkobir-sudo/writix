"""
Django shell script to fix TeacherAttendance status column length
Run this with: python manage.py shell < fix_attendance_status_column.py
"""

from django.db import connection

def fix_status_column():
    """Update the status column to allow longer values"""

    with connection.cursor() as cursor:
        # Get database vendor
        db_vendor = connection.vendor

        print(f"Database: {db_vendor}")
        print("Updating student_management_teacherattendance.status column...")

        try:
            if db_vendor == 'postgresql':
                # PostgreSQL syntax
                cursor.execute("""
                    ALTER TABLE student_management_teacherattendance
                    ALTER COLUMN status TYPE VARCHAR(20);
                """)
                print("✓ PostgreSQL: Status column updated to VARCHAR(20)")

            elif db_vendor == 'mysql':
                # MySQL syntax
                cursor.execute("""
                    ALTER TABLE student_management_teacherattendance
                    MODIFY COLUMN status VARCHAR(20);
                """)
                print("✓ MySQL: Status column updated to VARCHAR(20)")

            elif db_vendor == 'sqlite':
                # SQLite doesn't support ALTER COLUMN directly
                # We need to check current schema first
                cursor.execute("PRAGMA table_info(student_management_teacherattendance);")
                columns = cursor.fetchall()

                print("Current columns:", columns)
                print("\nSQLite detected. Creating backup and recreating table...")

                # For SQLite, we need to recreate the table
                cursor.execute("""
                    CREATE TABLE student_management_teacherattendance_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        teacher_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        marked_by_id INTEGER,
                        marked_at DATETIME,
                        check_in_time TIME,
                        check_out_time TIME,
                        working_hours DECIMAL(4,2) DEFAULT 0,
                        overtime_hours DECIMAL(4,2) DEFAULT 0,
                        remarks TEXT,
                        created_at DATETIME,
                        updated_at DATETIME,
                        FOREIGN KEY (teacher_id) REFERENCES student_management_teacher(id),
                        FOREIGN KEY (marked_by_id) REFERENCES auth_user(id),
                        UNIQUE (teacher_id, date)
                    );
                """)

                # Copy data
                cursor.execute("""
                    INSERT INTO student_management_teacherattendance_new
                    SELECT * FROM student_management_teacherattendance;
                """)

                # Drop old table
                cursor.execute("DROP TABLE student_management_teacherattendance;")

                # Rename new table
                cursor.execute("""
                    ALTER TABLE student_management_teacherattendance_new
                    RENAME TO student_management_teacherattendance;
                """)

                print("✓ SQLite: Table recreated with VARCHAR(20) status column")

            else:
                print(f"✗ Unsupported database: {db_vendor}")
                print("Please update manually or use Django migrations")
                return False

            print("\n✓ Successfully updated status column!")
            print("You can now save attendance records with: present, absent, late, leave")
            return True

        except Exception as e:
            print(f"\n✗ Error updating column: {e}")
            print("\nAlternative: Update your models.py and run:")
            print("  python manage.py makemigrations student_management")
            print("  python manage.py migrate student_management")
            return False

# Run the fix
if __name__ == '__main__':
    fix_status_column()
else:
    # When run via shell
    fix_status_column()
