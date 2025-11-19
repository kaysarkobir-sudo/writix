"""
Django shell script to create Driver table if not exists
Run this with: python manage.py shell < create_driver_table.py
"""

from django.db import connection

def create_driver_table():
    """Create student_management_driver table if it doesn't exist"""

    with connection.cursor() as cursor:
        db_vendor = connection.vendor
        print(f"Database: {db_vendor}")
        print(f"{'='*70}")
        print("Creating Driver table if not exists...")
        print(f"{'='*70}\n")

        try:
            if db_vendor == 'postgresql':
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'student_management_driver'
                    );
                """)

                table_exists = cursor.fetchone()[0]

                if table_exists:
                    print("✓ Driver table already exists")
                    return True

                # Create table
                cursor.execute("""
                    CREATE TABLE student_management_driver (
                        id SERIAL PRIMARY KEY,
                        school_id BIGINT NOT NULL REFERENCES student_management_institution(id) ON DELETE CASCADE,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        employee_id VARCHAR(50) NOT NULL UNIQUE,
                        phone_number VARCHAR(15) NOT NULL,
                        email VARCHAR(254) NULL,
                        license_number VARCHAR(50) NOT NULL UNIQUE,
                        license_expiry DATE NOT NULL,
                        address TEXT DEFAULT '',
                        date_of_birth DATE NULL,
                        date_of_joining DATE NULL,
                        photo VARCHAR(100) NULL,
                        status VARCHAR(20) DEFAULT 'active',
                        emergency_contact VARCHAR(15) DEFAULT '',
                        blood_group VARCHAR(10) DEFAULT '',
                        experience_years INTEGER DEFAULT 0,
                        salary DECIMAL(10,2) DEFAULT 0,
                        notes TEXT DEFAULT ''
                    );
                """)

                # Create indexes
                cursor.execute("""
                    CREATE INDEX idx_driver_school_id
                    ON student_management_driver(school_id);
                """)

                cursor.execute("""
                    CREATE INDEX idx_driver_status
                    ON student_management_driver(status);
                """)

                cursor.execute("""
                    CREATE INDEX idx_driver_employee_id
                    ON student_management_driver(employee_id);
                """)

                print("✓ PostgreSQL: Driver table created successfully")

            elif db_vendor == 'mysql':
                # Check if table exists
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_name = 'student_management_driver';
                """)

                table_exists = cursor.fetchone()[0] > 0

                if table_exists:
                    print("✓ Driver table already exists")
                    return True

                # Create table
                cursor.execute("""
                    CREATE TABLE student_management_driver (
                        id BIGINT AUTO_INCREMENT PRIMARY KEY,
                        school_id BIGINT NOT NULL,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        employee_id VARCHAR(50) NOT NULL UNIQUE,
                        phone_number VARCHAR(15) NOT NULL,
                        email VARCHAR(254) NULL,
                        license_number VARCHAR(50) NOT NULL UNIQUE,
                        license_expiry DATE NOT NULL,
                        address TEXT,
                        date_of_birth DATE NULL,
                        date_of_joining DATE NULL,
                        photo VARCHAR(100) NULL,
                        status VARCHAR(20) DEFAULT 'active',
                        emergency_contact VARCHAR(15) DEFAULT '',
                        blood_group VARCHAR(10) DEFAULT '',
                        experience_years INT DEFAULT 0,
                        salary DECIMAL(10,2) DEFAULT 0,
                        notes TEXT,
                        FOREIGN KEY (school_id)
                            REFERENCES student_management_institution(id)
                            ON DELETE CASCADE,
                        INDEX idx_driver_school_id (school_id),
                        INDEX idx_driver_status (status),
                        INDEX idx_driver_employee_id (employee_id)
                    );
                """)

                print("✓ MySQL: Driver table created successfully")

            elif db_vendor == 'sqlite':
                # Check if table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='student_management_driver';
                """)

                if cursor.fetchone():
                    print("✓ Driver table already exists")
                    return True

                # Create table
                cursor.execute("""
                    CREATE TABLE student_management_driver (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        school_id INTEGER NOT NULL,
                        first_name VARCHAR(100) NOT NULL,
                        last_name VARCHAR(100) NOT NULL,
                        employee_id VARCHAR(50) NOT NULL UNIQUE,
                        phone_number VARCHAR(15) NOT NULL,
                        email VARCHAR(254) NULL,
                        license_number VARCHAR(50) NOT NULL UNIQUE,
                        license_expiry DATE NOT NULL,
                        address TEXT DEFAULT '',
                        date_of_birth DATE NULL,
                        date_of_joining DATE NULL,
                        photo VARCHAR(100) NULL,
                        status VARCHAR(20) DEFAULT 'active',
                        emergency_contact VARCHAR(15) DEFAULT '',
                        blood_group VARCHAR(10) DEFAULT '',
                        experience_years INTEGER DEFAULT 0,
                        salary DECIMAL(10,2) DEFAULT 0,
                        notes TEXT DEFAULT '',
                        FOREIGN KEY (school_id)
                            REFERENCES student_management_institution(id)
                            ON DELETE CASCADE
                    );
                """)

                # Create indexes
                cursor.execute("""
                    CREATE INDEX idx_driver_school_id
                    ON student_management_driver(school_id);
                """)

                cursor.execute("""
                    CREATE INDEX idx_driver_status
                    ON student_management_driver(status);
                """)

                cursor.execute("""
                    CREATE INDEX idx_driver_employee_id
                    ON student_management_driver(employee_id);
                """)

                print("✓ SQLite: Driver table created successfully")

            else:
                print(f"✗ Unsupported database: {db_vendor}")
                return False

            print("\n" + "="*70)
            print("✓ Driver table created successfully!")
            print("="*70)
            print("\nTable structure:")
            print("  - id (Primary Key)")
            print("  - school_id (Foreign Key to Institution)")
            print("  - first_name, last_name")
            print("  - employee_id (Unique)")
            print("  - phone_number, email")
            print("  - license_number (Unique), license_expiry")
            print("  - address, date_of_birth, date_of_joining")
            print("  - photo (image path)")
            print("  - status (active/inactive/on_leave)")
            print("  - emergency_contact, blood_group")
            print("  - experience_years, salary")
            print("  - notes")
            print("\nYou can now add drivers to your transport system!")
            return True

        except Exception as e:
            print(f"\n✗ Error creating table: {e}")
            print("\nAlternative: Use Django migrations:")
            print("  1. Add Driver model to your models.py")
            print("  2. Run: python manage.py makemigrations student_management")
            print("  3. Run: python manage.py migrate student_management")
            return False

# Run the creation
if __name__ == '__main__':
    create_driver_table()
else:
    create_driver_table()
