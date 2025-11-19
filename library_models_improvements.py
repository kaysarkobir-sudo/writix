"""
Suggested improvements for Library Management Models
Add these fields to your existing models in models.py
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

# Enhanced Book Model
class Book(models.Model):
    BOOK_STATUS = [
        ('available', 'Available'),
        ('issued', 'Issued'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
    ]

    CATEGORY_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('mathematics', 'Mathematics'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('literature', 'Literature'),
        ('biography', 'Biography'),
        ('reference', 'Reference'),
        ('other', 'Other'),
    ]

    # Basic Information
    name = models.CharField(max_length=200, verbose_name="Book Title")
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, blank=True, unique=True, verbose_name="ISBN")
    edition = models.CharField(max_length=50, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)

    # Categorization
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    subject_code = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=50, default='English')

    # Physical Details
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(default=1, help_text="Auto-updated on issue/return")
    rack_no = models.CharField(max_length=50, blank=True, verbose_name="Rack Number")
    shelf_location = models.CharField(max_length=100, blank=True)

    # Additional Info
    pages = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='library/covers/', blank=True, null=True)
    barcode = models.CharField(max_length=50, blank=True, unique=True)

    # Tracking
    date_added = models.DateField(default=timezone.now)
    last_issued = models.DateField(null=True, blank=True)
    total_issued_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.name} by {self.author}"

    @property
    def is_available(self):
        return self.available_quantity > 0


# Enhanced LibraryMember Model
class LibraryMember(models.Model):
    MEMBERSHIP_STATUS = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
    ]

    student = models.OneToOneField('Student', on_delete=models.CASCADE, related_name='library_member')
    library_id = models.CharField(max_length=20, unique=True, verbose_name="Library Card Number")
    joined_on = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True, help_text="Membership expiry date")
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='active')

    # Limits
    max_books_allowed = models.PositiveIntegerField(default=3)
    current_books_count = models.PositiveIntegerField(default=0)

    # Tracking
    total_books_borrowed = models.PositiveIntegerField(default=0)
    total_fines_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    outstanding_fine = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Library Member"
        verbose_name_plural = "Library Members"

    def __str__(self):
        return f"{self.student} ({self.library_id})"

    @property
    def can_borrow(self):
        return (self.status == 'active' and
                self.current_books_count < self.max_books_allowed and
                self.outstanding_fine == 0)


# Enhanced IssueReturn Model
class IssueReturn(models.Model):
    STATUS_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    ]

    member = models.ForeignKey(LibraryMember, on_delete=models.CASCADE, related_name='issued_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issue_records')

    # Issue Details
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    expected_return_date = models.DateField(null=True, blank=True)

    # Return Details
    return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)

    # Status & Condition
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    condition_at_issue = models.CharField(max_length=50, default='Good')
    condition_at_return = models.CharField(max_length=50, blank=True)

    # Fines
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    fine_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)

    # Staff
    issued_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='books_issued')
    returned_to = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='books_received')

    remarks = models.TextField(blank=True)

    class Meta:
        verbose_name = "Issue / Return"
        verbose_name_plural = "Issues & Returns"
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.book.name} → {self.member.student}"

    def calculate_fine(self):
        """Calculate fine for overdue books"""
        if self.return_date and self.due_date:
            if self.return_date > self.due_date:
                overdue_days = (self.return_date - self.due_date).days
                return overdue_days * float(self.fine_per_day)
        elif not self.return_date and timezone.now().date() > self.due_date:
            overdue_days = (timezone.now().date() - self.due_date).days
            return overdue_days * float(self.fine_per_day)
        return 0

    def save(self, *args, **kwargs):
        # Auto-calculate fine
        if not self.fine_amount:
            self.fine_amount = self.calculate_fine()

        # Update status
        if self.return_date:
            self.status = 'returned'
        elif timezone.now().date() > self.due_date:
            self.status = 'overdue'

        super().save(*args, **kwargs)


# Enhanced EBook Model
class EBook(models.Model):
    EBOOK_FORMAT = [
        ('pdf', 'PDF'),
        ('epub', 'EPUB'),
        ('mobi', 'MOBI'),
        ('txt', 'TXT'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    file = models.FileField(upload_to='ebooks/')
    cover_image = models.ImageField(upload_to='ebooks/covers/', blank=True, null=True)

    # Details
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    format = models.CharField(max_length=10, choices=EBOOK_FORMAT, default='pdf')
    file_size = models.CharField(max_length=50, blank=True, help_text="e.g., 5.2 MB")
    pages = models.PositiveIntegerField(null=True, blank=True)

    # Access
    is_public = models.BooleanField(default=True, help_text="Available to all members")
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    # Metadata
    uploaded_on = models.DateField(default=timezone.now)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "E-Book"
        verbose_name_plural = "E-Books"
        ordering = ['-uploaded_on']

    def __str__(self):
        return self.title
