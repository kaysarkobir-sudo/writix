# Library Management Dashboard Integration Guide

This guide provides complete copy-paste ready code to integrate Library Management statistics into your main dashboard.

## Step 1: Add Required Imports to views.py

Add these imports at the top of your `student_management/views.py` file (if not already present):

```python
from .models import Book, LibraryMember, IssueReturn, EBook
```

**Complete import section should include:**

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone
from .models import (
    Student, AcademicClass, Section, ParentProfile,
    AttendanceSession, FeeInvoice, FeePayment,
    Vehicle, TransportRoute, TransportMember,
    Book, LibraryMember, IssueReturn, EBook,
    Institution
)
```

---

## Step 2: Replace main_dashboard View Function

**Location:** `student_management/views.py`

**Find the existing `main_dashboard` function and replace it completely with this:**

```python
@login_required
def main_dashboard(request):
    """Enhanced main dashboard with all statistics"""

    # Get user's institution (if applicable)
    try:
        if hasattr(request.user, 'profile'):
            user_institution = request.user.profile.institution
        else:
            user_institution = Institution.objects.first()
    except:
        user_institution = None

    # Basic Statistics
    total_students = Student.objects.filter(current_status='active').count()
    total_classes = AcademicClass.objects.count()
    total_sections = Section.objects.count()
    total_parents = ParentProfile.objects.count()

    # Recent Students - Use 'id' instead of 'created_at' since created_at doesn't exist
    recent_students = Student.objects.filter(
        current_status='active'
    ).order_by('-id')[:5]  # Changed from '-created_at' to '-id'

    # Class Distribution
    try:
        class_distribution = AcademicClass.objects.annotate(
            student_count=Count('student')
        ).order_by('class_name')
    except:
        class_distribution = []

    # Gender Distribution
    try:
        gender_distribution = Student.objects.filter(
            current_status='active'
        ).values('gender').annotate(count=Count('id'))
    except:
        gender_distribution = []

    # Status Distribution
    try:
        status_distribution = Student.objects.values(
            'current_status'
        ).annotate(count=Count('id'))
    except:
        status_distribution = []

    # ===== ATTENDANCE STATISTICS =====
    today = timezone.now().date()

    # Today's attendance
    try:
        today_sessions = AttendanceSession.objects.filter(date=today)
        today_total_students = today_sessions.aggregate(
            total=Sum('total_students')
        )['total'] or 0

        today_present = today_sessions.aggregate(
            total=Sum('present_count')
        )['total'] or 0

        today_absent_count = today_sessions.aggregate(
            total=Sum('absent_count')
        )['total'] or 0

        if today_total_students > 0:
            today_attendance_percentage = round((today_present / today_total_students * 100), 1)
        else:
            today_attendance_percentage = 0
    except:
        today_attendance_percentage = 0
        today_absent_count = 0
        today_present = 0
        today_total_students = 0

    # ===== FEE STATISTICS =====
    try:
        # Total expected fees
        total_expected = FeeInvoice.objects.aggregate(
            total=Sum('amount_due')
        )['total'] or 0

        # Total collected
        total_collected = FeePayment.objects.filter(
            verified=True
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Pending fees
        pending_fees = FeeInvoice.objects.filter(
            status__in=['pending', 'overdue']
        ).aggregate(
            total=Sum('balance')
        )['total'] or 0

        # Overdue invoices count
        overdue_invoices = FeeInvoice.objects.filter(
            status='overdue'
        ).count()
    except:
        total_expected = 0
        total_collected = 0
        pending_fees = 0
        overdue_invoices = 0

    # ===== TRANSPORT STATISTICS =====
    try:
        # Get transport statistics filtered by institution if available
        if user_institution:
            total_buses = Vehicle.objects.filter(school=user_institution).count()
            total_routes = TransportRoute.objects.filter(school=user_institution).count()
            total_transport_members = TransportMember.objects.filter(school=user_institution).count()
        else:
            total_buses = Vehicle.objects.count()
            total_routes = TransportRoute.objects.count()
            total_transport_members = TransportMember.objects.count()
    except:
        total_buses = 0
        total_routes = 0
        total_transport_members = 0

    # ===== LIBRARY STATISTICS =====
    try:
        # Total books in library
        total_books = Book.objects.count()

        # Available books
        available_books = Book.objects.filter(available_quantity__gt=0).count()

        # Total library members
        total_library_members = LibraryMember.objects.count()

        # Active library members
        active_library_members = LibraryMember.objects.filter(status='active').count()

        # Currently issued books (not returned)
        issued_books = IssueReturn.objects.filter(
            status__in=['issued', 'overdue']
        ).count()

        # Overdue books
        overdue_books = IssueReturn.objects.filter(status='overdue').count()

        # Total e-books
        total_ebooks = EBook.objects.count()

        # Books issued today
        books_issued_today = IssueReturn.objects.filter(issue_date=today).count()

        # Books returned today
        books_returned_today = IssueReturn.objects.filter(return_date=today).count()
    except:
        total_books = 0
        available_books = 0
        total_library_members = 0
        active_library_members = 0
        issued_books = 0
        overdue_books = 0
        total_ebooks = 0
        books_issued_today = 0
        books_returned_today = 0

    context = {
        # Basic Stats
        'total_students': total_students,
        'total_classes': total_classes,
        'total_sections': total_sections,
        'total_parents': total_parents,

        # Student Data
        'recent_students': recent_students,
        'class_distribution': class_distribution,
        'gender_distribution': gender_distribution,
        'status_distribution': status_distribution,

        # Attendance Stats
        'today_attendance_percentage': today_attendance_percentage,
        'today_absent_count': today_absent_count,
        'today_present': today_present,
        'today_total_students': today_total_students,

        # Fee Stats
        'total_collected': total_collected,
        'pending_fees': pending_fees,
        'total_expected': total_expected,
        'overdue_invoices': overdue_invoices,

        # Transport Stats
        'total_buses': total_buses,
        'total_routes': total_routes,
        'total_transport_members': total_transport_members,

        # Library Stats
        'total_books': total_books,
        'available_books': available_books,
        'total_library_members': total_library_members,
        'active_library_members': active_library_members,
        'issued_books': issued_books,
        'overdue_books': overdue_books,
        'total_ebooks': total_ebooks,
        'books_issued_today': books_issued_today,
        'books_returned_today': books_returned_today,
    }

    return render(request, 'student_management/main_dashboard.html', context)
```

---

## Step 3: Update Dashboard Card HTML

**Location:** `templates/student_management/main_dashboard.html`

**Find your Library Management card and replace it with:**

```html
<!-- Library Management Card -->
<div class="dashboard-card fade-in" style="--gradient-start: #84cc16; --gradient-end: #65a30d; animation-delay: 0.9s;" onclick="window.location.href='{% url 'library_panel' %}'">
    <div>
        <div class="card-icon">
            📖
        </div>
        <h3 class="card-title">Library Management</h3>
        <p class="card-description">
            Manage books, track borrowing, handle returns, and maintain library records.
        </p>
    </div>
    <div class="card-stats">
        <div class="stat-item">
            <span class="stat-value">{{ total_books|default:"0" }}</span>
            <span class="stat-label">Books</span>
        </div>
        <div class="stat-item">
            <span class="stat-value">{{ issued_books|default:"0" }}</span>
            <span class="stat-label">Issued</span>
        </div>
    </div>
</div>
```

---

## Step 4: Verify Library URLs

Make sure your `student_management/urls.py` has the library URL pattern:

```python
# Library Management URLs
path('library/', library_panel, name='library_panel'),
```

---

## Available Library Statistics

After integration, these statistics are available in your dashboard template:

### Basic Counts:
- `{{ total_books }}` - Total books in library
- `{{ available_books }}` - Books available for borrowing
- `{{ issued_books }}` - Currently issued books
- `{{ overdue_books }}` - Overdue books

### Member Statistics:
- `{{ total_library_members }}` - Total library members
- `{{ active_library_members }}` - Active members only

### Daily Statistics:
- `{{ books_issued_today }}` - Books issued today
- `{{ books_returned_today }}` - Books returned today

### Digital Collection:
- `{{ total_ebooks }}` - Total e-books

---

## Alternative Card Layouts

### Option 1: Three Stats Layout

```html
<div class="card-stats">
    <div class="stat-item">
        <span class="stat-value">{{ total_books|default:"0" }}</span>
        <span class="stat-label">Books</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">{{ issued_books|default:"0" }}</span>
        <span class="stat-label">Issued</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">{{ overdue_books|default:"0" }}</span>
        <span class="stat-label">Overdue</span>
    </div>
</div>
```

### Option 2: Members and E-Books

```html
<div class="card-stats">
    <div class="stat-item">
        <span class="stat-value">{{ active_library_members|default:"0" }}</span>
        <span class="stat-label">Members</span>
    </div>
    <div class="stat-item">
        <span class="stat-value">{{ total_ebooks|default:"0" }}</span>
        <span class="stat-label">E-Books</span>
    </div>
</div>
```

---

## Testing

After implementing the changes:

1. **Restart Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Navigate to main dashboard:**
   - Go to your dashboard URL
   - Library card should display book count and issued books count
   - Click the card to navigate to Library Management panel

3. **Verify statistics:**
   - Add some books to library
   - Register library members
   - Issue some books
   - Check if dashboard stats update correctly

---

## Troubleshooting

### Issue: "Book model not found"
**Solution:** Make sure you've created the library tables:
```bash
python manage.py shell < create_library_tables.py
```

### Issue: "library_panel URL not found"
**Solution:** Check your `urls.py` has the library URL pattern defined

### Issue: Stats showing 0
**Solution:**
- This is normal if no data exists
- Add books and library members to see actual statistics
- The try-except blocks prevent errors when tables are empty

---

## What's Changed

### Added to View:
- ✅ Library statistics calculation section
- ✅ 9 new context variables for library stats
- ✅ Exception handling for missing library data
- ✅ All existing functionality preserved

### Added to Template:
- ✅ Working URL link to library panel
- ✅ Dynamic book count display
- ✅ Dynamic issued books count display

### What's NOT Changed:
- ✅ All existing dashboard statistics (students, attendance, fees, transport)
- ✅ All existing template structure
- ✅ All existing card styles and animations
- ✅ All existing functionality

---

## Summary

This integration adds comprehensive library statistics to your main dashboard while preserving all existing functionality. The library card will now:

1. Display accurate book counts from your database
2. Show currently issued books count
3. Navigate to the library management panel when clicked
4. Match your existing glassmorphism design theme

All statistics are safely wrapped in try-except blocks, so the dashboard will continue working even if library tables don't exist yet.
