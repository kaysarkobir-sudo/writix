"""
Django shell script to create Library Management tables if not exist
Run this with: python manage.py shell < create_library_tables.py
"""

from django.db import connection

def create_library_tables():
    """Create all library management tables if they don't exist"""

    with connection.cursor() as cursor:
        db_vendor = connection.vendor
        print(f"Database: {db_vendor}")
        print(f"{'='*70}")
        print("Creating Library Management tables if not exist...")
        print(f"{'='*70}\n")

        try:
            # =================================================================
            # 1. CREATE BOOK TABLE
            # =================================================================
            print("Checking Book table...")

            if db_vendor == 'postgresql':
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'student_management_book'
                    );
                """)
                table_exists = cursor.fetchone()[0]

                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE student_management_book (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(200) NOT NULL,
                            author VARCHAR(200) NOT NULL,
                            publisher VARCHAR(200) DEFAULT '',
                            isbn VARCHAR(13) UNIQUE,
                            edition VARCHAR(50) DEFAULT '',
                            publication_year INTEGER NULL,
                            category VARCHAR(50) DEFAULT 'other',
                            subject_code VARCHAR(50) DEFAULT '',
                            language VARCHAR(50) DEFAULT 'English',
                            price DECIMAL(8,2) NOT NULL,
                            quantity INTEGER DEFAULT 1,
                            available_quantity INTEGER DEFAULT 1,
                            rack_no VARCHAR(50) DEFAULT '',
                            shelf_location VARCHAR(100) DEFAULT '',
                            pages INTEGER NULL,
                            description TEXT DEFAULT '',
                            cover_image VARCHAR(100) NULL,
                            barcode VARCHAR(50) UNIQUE,
                            date_added DATE DEFAULT CURRENT_DATE,
                            last_issued DATE NULL,
                            total_issued_count INTEGER DEFAULT 0
                        );
                    """)

                    # Create indexes
                    cursor.execute("CREATE INDEX idx_book_category ON student_management_book(category);")
                    cursor.execute("CREATE INDEX idx_book_author ON student_management_book(author);")
                    cursor.execute("CREATE INDEX idx_book_name ON student_management_book(name);")

                    print("✓ PostgreSQL: Book table created successfully")
                else:
                    print("✓ Book table already exists")

            elif db_vendor == 'mysql':
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = 'student_management_book';
                """)
                table_exists = cursor.fetchone()[0] > 0

                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE student_management_book (
                            id BIGINT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(200) NOT NULL,
                            author VARCHAR(200) NOT NULL,
                            publisher VARCHAR(200) DEFAULT '',
                            isbn VARCHAR(13) UNIQUE,
                            edition VARCHAR(50) DEFAULT '',
                            publication_year INT NULL,
                            category VARCHAR(50) DEFAULT 'other',
                            subject_code VARCHAR(50) DEFAULT '',
                            language VARCHAR(50) DEFAULT 'English',
                            price DECIMAL(8,2) NOT NULL,
                            quantity INT DEFAULT 1,
                            available_quantity INT DEFAULT 1,
                            rack_no VARCHAR(50) DEFAULT '',
                            shelf_location VARCHAR(100) DEFAULT '',
                            pages INT NULL,
                            description TEXT,
                            cover_image VARCHAR(100) NULL,
                            barcode VARCHAR(50) UNIQUE,
                            date_added DATE DEFAULT (CURRENT_DATE),
                            last_issued DATE NULL,
                            total_issued_count INT DEFAULT 0,
                            INDEX idx_book_category (category),
                            INDEX idx_book_author (author),
                            INDEX idx_book_name (name)
                        );
                    """)
                    print("✓ MySQL: Book table created successfully")
                else:
                    print("✓ Book table already exists")

            elif db_vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='student_management_book';
                """)

                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE student_management_book (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name VARCHAR(200) NOT NULL,
                            author VARCHAR(200) NOT NULL,
                            publisher VARCHAR(200) DEFAULT '',
                            isbn VARCHAR(13) UNIQUE,
                            edition VARCHAR(50) DEFAULT '',
                            publication_year INTEGER NULL,
                            category VARCHAR(50) DEFAULT 'other',
                            subject_code VARCHAR(50) DEFAULT '',
                            language VARCHAR(50) DEFAULT 'English',
                            price DECIMAL(8,2) NOT NULL,
                            quantity INTEGER DEFAULT 1,
                            available_quantity INTEGER DEFAULT 1,
                            rack_no VARCHAR(50) DEFAULT '',
                            shelf_location VARCHAR(100) DEFAULT '',
                            pages INTEGER NULL,
                            description TEXT DEFAULT '',
                            cover_image VARCHAR(100) NULL,
                            barcode VARCHAR(50) UNIQUE,
                            date_added DATE DEFAULT CURRENT_DATE,
                            last_issued DATE NULL,
                            total_issued_count INTEGER DEFAULT 0
                        );
                    """)

                    cursor.execute("CREATE INDEX idx_book_category ON student_management_book(category);")
                    cursor.execute("CREATE INDEX idx_book_author ON student_management_book(author);")
                    cursor.execute("CREATE INDEX idx_book_name ON student_management_book(name);")

                    print("✓ SQLite: Book table created successfully")
                else:
                    print("✓ Book table already exists")

            # =================================================================
            # 2. CREATE LIBRARY MEMBER TABLE
            # =================================================================
            print("\nChecking LibraryMember table...")

            if db_vendor == 'postgresql':
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'student_management_librarymember'
                    );
                """)
                table_exists = cursor.fetchone()[0]

                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE student_management_librarymember (
                            id SERIAL PRIMARY KEY,
                            student_id BIGINT NOT NULL UNIQUE REFERENCES student_management_student(id) ON DELETE CASCADE,
                            library_id VARCHAR(20) NOT NULL UNIQUE,
                            joined_on DATE DEFAULT CURRENT_DATE,
                            valid_until DATE NULL,
                            status VARCHAR(20) DEFAULT 'active',
                            max_books_allowed INTEGER DEFAULT 3,
                            current_books_count INTEGER DEFAULT 0,
                            total_books_borrowed INTEGER DEFAULT 0,
                            total_fines_paid DECIMAL(8,2) DEFAULT 0,
                            outstanding_fine DECIMAL(8,2) DEFAULT 0,
                            notes TEXT DEFAULT ''
                        );
                    """)

                    cursor.execute("CREATE INDEX idx_librarymember_status ON student_management_librarymember(status);")
                    cursor.execute("CREATE INDEX idx_librarymember_student ON student_management_librarymember(student_id);")

                    print("✓ PostgreSQL: LibraryMember table created successfully")
                else:
                    print("✓ LibraryMember table already exists")

            elif db_vendor == 'mysql':
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = 'student_management_librarymember';
                """)
                table_exists = cursor.fetchone()[0] > 0

                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE student_management_librarymember (
                            id BIGINT AUTO_INCREMENT PRIMARY KEY,
                            student_id BIGINT NOT NULL UNIQUE,
                            library_id VARCHAR(20) NOT NULL UNIQUE,
                            joined_on DATE DEFAULT (CURRENT_DATE),
                            valid_until DATE NULL,
                            status VARCHAR(20) DEFAULT 'active',
                            max_books_allowed INT DEFAULT 3,
                            current_books_count INT DEFAULT 0,
                            total_books_borrowed INT DEFAULT 0,
                            total_fines_paid DECIMAL(8,2) DEFAULT 0,
                            outstanding_fine DECIMAL(8,2) DEFAULT 0,
                            notes TEXT,
                            FOREIGN KEY (student_id) REFERENCES student_management_student(id) ON DELETE CASCADE,
                            INDEX idx_librarymember_status (status),
                            INDEX idx_librarymember_student (student_id)
                        );
                    """)
                    print("✓ MySQL: LibraryMember table created successfully")
                else:
                    print("✓ LibraryMember table already exists")

            elif db_vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='student_management_librarymember';
                """)

                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE student_management_librarymember (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            student_id INTEGER NOT NULL UNIQUE,
                            library_id VARCHAR(20) NOT NULL UNIQUE,
                            joined_on DATE DEFAULT CURRENT_DATE,
                            valid_until DATE NULL,
                            status VARCHAR(20) DEFAULT 'active',
                            max_books_allowed INTEGER DEFAULT 3,
                            current_books_count INTEGER DEFAULT 0,
                            total_books_borrowed INTEGER DEFAULT 0,
                            total_fines_paid DECIMAL(8,2) DEFAULT 0,
                            outstanding_fine DECIMAL(8,2) DEFAULT 0,
                            notes TEXT DEFAULT '',
                            FOREIGN KEY (student_id) REFERENCES student_management_student(id) ON DELETE CASCADE
                        );
                    """)

                    cursor.execute("CREATE INDEX idx_librarymember_status ON student_management_librarymember(status);")
                    cursor.execute("CREATE INDEX idx_librarymember_student ON student_management_librarymember(student_id);")

                    print("✓ SQLite: LibraryMember table created successfully")
                else:
                    print("✓ LibraryMember table already exists")

            # =================================================================
            # 3. CREATE ISSUE RETURN TABLE
            # =================================================================
            print("\nChecking IssueReturn table...")

            if db_vendor == 'postgresql':
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'student_management_issuereturn'
                    );
                """)
                table_exists = cursor.fetchone()[0]

                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE student_management_issuereturn (
                            id SERIAL PRIMARY KEY,
                            member_id BIGINT NOT NULL REFERENCES student_management_librarymember(id) ON DELETE CASCADE,
                            book_id BIGINT NOT NULL REFERENCES student_management_book(id) ON DELETE CASCADE,
                            issue_date DATE DEFAULT CURRENT_DATE,
                            due_date DATE NOT NULL,
                            expected_return_date DATE NULL,
                            return_date DATE NULL,
                            actual_return_date DATE NULL,
                            status VARCHAR(20) DEFAULT 'issued',
                            condition_at_issue VARCHAR(50) DEFAULT 'Good',
                            condition_at_return VARCHAR(50) DEFAULT '',
                            fine_amount DECIMAL(6,2) DEFAULT 0,
                            fine_paid BOOLEAN DEFAULT FALSE,
                            fine_per_day DECIMAL(5,2) DEFAULT 5.00,
                            issued_by_id INTEGER NULL REFERENCES auth_user(id) ON DELETE SET NULL,
                            returned_to_id INTEGER NULL REFERENCES auth_user(id) ON DELETE SET NULL,
                            remarks TEXT DEFAULT ''
                        );
                    """)

                    cursor.execute("CREATE INDEX idx_issuereturn_status ON student_management_issuereturn(status);")
                    cursor.execute("CREATE INDEX idx_issuereturn_member ON student_management_issuereturn(member_id);")
                    cursor.execute("CREATE INDEX idx_issuereturn_book ON student_management_issuereturn(book_id);")
                    cursor.execute("CREATE INDEX idx_issuereturn_issue_date ON student_management_issuereturn(issue_date);")

                    print("✓ PostgreSQL: IssueReturn table created successfully")
                else:
                    print("✓ IssueReturn table already exists")

            elif db_vendor == 'mysql':
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = 'student_management_issuereturn';
                """)
                table_exists = cursor.fetchone()[0] > 0

                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE student_management_issuereturn (
                            id BIGINT AUTO_INCREMENT PRIMARY KEY,
                            member_id BIGINT NOT NULL,
                            book_id BIGINT NOT NULL,
                            issue_date DATE DEFAULT (CURRENT_DATE),
                            due_date DATE NOT NULL,
                            expected_return_date DATE NULL,
                            return_date DATE NULL,
                            actual_return_date DATE NULL,
                            status VARCHAR(20) DEFAULT 'issued',
                            condition_at_issue VARCHAR(50) DEFAULT 'Good',
                            condition_at_return VARCHAR(50) DEFAULT '',
                            fine_amount DECIMAL(6,2) DEFAULT 0,
                            fine_paid BOOLEAN DEFAULT FALSE,
                            fine_per_day DECIMAL(5,2) DEFAULT 5.00,
                            issued_by_id INT NULL,
                            returned_to_id INT NULL,
                            remarks TEXT,
                            FOREIGN KEY (member_id) REFERENCES student_management_librarymember(id) ON DELETE CASCADE,
                            FOREIGN KEY (book_id) REFERENCES student_management_book(id) ON DELETE CASCADE,
                            FOREIGN KEY (issued_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
                            FOREIGN KEY (returned_to_id) REFERENCES auth_user(id) ON DELETE SET NULL,
                            INDEX idx_issuereturn_status (status),
                            INDEX idx_issuereturn_member (member_id),
                            INDEX idx_issuereturn_book (book_id),
                            INDEX idx_issuereturn_issue_date (issue_date)
                        );
                    """)
                    print("✓ MySQL: IssueReturn table created successfully")
                else:
                    print("✓ IssueReturn table already exists")

            elif db_vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='student_management_issuereturn';
                """)

                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE student_management_issuereturn (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            member_id INTEGER NOT NULL,
                            book_id INTEGER NOT NULL,
                            issue_date DATE DEFAULT CURRENT_DATE,
                            due_date DATE NOT NULL,
                            expected_return_date DATE NULL,
                            return_date DATE NULL,
                            actual_return_date DATE NULL,
                            status VARCHAR(20) DEFAULT 'issued',
                            condition_at_issue VARCHAR(50) DEFAULT 'Good',
                            condition_at_return VARCHAR(50) DEFAULT '',
                            fine_amount DECIMAL(6,2) DEFAULT 0,
                            fine_paid BOOLEAN DEFAULT 0,
                            fine_per_day DECIMAL(5,2) DEFAULT 5.00,
                            issued_by_id INTEGER NULL,
                            returned_to_id INTEGER NULL,
                            remarks TEXT DEFAULT '',
                            FOREIGN KEY (member_id) REFERENCES student_management_librarymember(id) ON DELETE CASCADE,
                            FOREIGN KEY (book_id) REFERENCES student_management_book(id) ON DELETE CASCADE,
                            FOREIGN KEY (issued_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
                            FOREIGN KEY (returned_to_id) REFERENCES auth_user(id) ON DELETE SET NULL
                        );
                    """)

                    cursor.execute("CREATE INDEX idx_issuereturn_status ON student_management_issuereturn(status);")
                    cursor.execute("CREATE INDEX idx_issuereturn_member ON student_management_issuereturn(member_id);")
                    cursor.execute("CREATE INDEX idx_issuereturn_book ON student_management_issuereturn(book_id);")
                    cursor.execute("CREATE INDEX idx_issuereturn_issue_date ON student_management_issuereturn(issue_date);")

                    print("✓ SQLite: IssueReturn table created successfully")
                else:
                    print("✓ IssueReturn table already exists")

            # =================================================================
            # 4. CREATE EBOOK TABLE
            # =================================================================
            print("\nChecking EBook table...")

            if db_vendor == 'postgresql':
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'student_management_ebook'
                    );
                """)
                table_exists = cursor.fetchone()[0]

                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE student_management_ebook (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(200) NOT NULL,
                            author VARCHAR(200) DEFAULT '',
                            file VARCHAR(100) NOT NULL,
                            cover_image VARCHAR(100) NULL,
                            description TEXT DEFAULT '',
                            category VARCHAR(50) DEFAULT '',
                            format VARCHAR(10) DEFAULT 'pdf',
                            file_size VARCHAR(50) DEFAULT '',
                            pages INTEGER NULL,
                            is_public BOOLEAN DEFAULT TRUE,
                            download_count INTEGER DEFAULT 0,
                            view_count INTEGER DEFAULT 0,
                            uploaded_on DATE DEFAULT CURRENT_DATE,
                            uploaded_by_id INTEGER NULL REFERENCES auth_user(id) ON DELETE SET NULL
                        );
                    """)

                    cursor.execute("CREATE INDEX idx_ebook_category ON student_management_ebook(category);")
                    cursor.execute("CREATE INDEX idx_ebook_format ON student_management_ebook(format);")
                    cursor.execute("CREATE INDEX idx_ebook_is_public ON student_management_ebook(is_public);")

                    print("✓ PostgreSQL: EBook table created successfully")
                else:
                    print("✓ EBook table already exists")

            elif db_vendor == 'mysql':
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.tables
                    WHERE table_name = 'student_management_ebook';
                """)
                table_exists = cursor.fetchone()[0] > 0

                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE student_management_ebook (
                            id BIGINT AUTO_INCREMENT PRIMARY KEY,
                            title VARCHAR(200) NOT NULL,
                            author VARCHAR(200) DEFAULT '',
                            file VARCHAR(100) NOT NULL,
                            cover_image VARCHAR(100) NULL,
                            description TEXT,
                            category VARCHAR(50) DEFAULT '',
                            format VARCHAR(10) DEFAULT 'pdf',
                            file_size VARCHAR(50) DEFAULT '',
                            pages INT NULL,
                            is_public BOOLEAN DEFAULT TRUE,
                            download_count INT DEFAULT 0,
                            view_count INT DEFAULT 0,
                            uploaded_on DATE DEFAULT (CURRENT_DATE),
                            uploaded_by_id INT NULL,
                            FOREIGN KEY (uploaded_by_id) REFERENCES auth_user(id) ON DELETE SET NULL,
                            INDEX idx_ebook_category (category),
                            INDEX idx_ebook_format (format),
                            INDEX idx_ebook_is_public (is_public)
                        );
                    """)
                    print("✓ MySQL: EBook table created successfully")
                else:
                    print("✓ EBook table already exists")

            elif db_vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='student_management_ebook';
                """)

                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE student_management_ebook (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title VARCHAR(200) NOT NULL,
                            author VARCHAR(200) DEFAULT '',
                            file VARCHAR(100) NOT NULL,
                            cover_image VARCHAR(100) NULL,
                            description TEXT DEFAULT '',
                            category VARCHAR(50) DEFAULT '',
                            format VARCHAR(10) DEFAULT 'pdf',
                            file_size VARCHAR(50) DEFAULT '',
                            pages INTEGER NULL,
                            is_public BOOLEAN DEFAULT 1,
                            download_count INTEGER DEFAULT 0,
                            view_count INTEGER DEFAULT 0,
                            uploaded_on DATE DEFAULT CURRENT_DATE,
                            uploaded_by_id INTEGER NULL,
                            FOREIGN KEY (uploaded_by_id) REFERENCES auth_user(id) ON DELETE SET NULL
                        );
                    """)

                    cursor.execute("CREATE INDEX idx_ebook_category ON student_management_ebook(category);")
                    cursor.execute("CREATE INDEX idx_ebook_format ON student_management_ebook(format);")
                    cursor.execute("CREATE INDEX idx_ebook_is_public ON student_management_ebook(is_public);")

                    print("✓ SQLite: EBook table created successfully")
                else:
                    print("✓ EBook table already exists")

            # =================================================================
            # SUMMARY
            # =================================================================
            print("\n" + "="*70)
            print("✓ All Library Management tables checked/created successfully!")
            print("="*70)
            print("\nTables created:")
            print("  1. student_management_book")
            print("     - Stores book information, inventory, and tracking")
            print("  2. student_management_librarymember")
            print("     - Manages library memberships and borrowing limits")
            print("  3. student_management_issuereturn")
            print("     - Tracks book issues, returns, and fines")
            print("  4. student_management_ebook")
            print("     - Manages digital e-book collection")
            print("\nYou can now use the Library Management System!")
            print("\nNext steps:")
            print("  1. Add books to the library")
            print("  2. Register library members")
            print("  3. Start issuing books")
            print("  4. Upload e-books")
            return True

        except Exception as e:
            print(f"\n✗ Error creating tables: {e}")
            print("\nAlternative: Use Django migrations:")
            print("  1. Add the models to your models.py")
            print("  2. Run: python manage.py makemigrations student_management")
            print("  3. Run: python manage.py migrate student_management")
            return False

# Run the creation
if __name__ == '__main__':
    create_library_tables()
else:
    create_library_tables()
