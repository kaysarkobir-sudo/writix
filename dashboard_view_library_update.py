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
