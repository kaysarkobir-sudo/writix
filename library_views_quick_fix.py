"""
Quick Fix for Library Views - Works with Minimal Table Structure
Replace the problematic view functions in your views.py with these
"""

# ============================================================================
# UPDATED EBOOK VIEWS (Works with minimal EBook table)
# ============================================================================

@login_required
def ebook_list(request):
    """List all e-books - UPDATED for minimal table structure"""
    # Use 'id' instead of 'uploaded_on' for ordering
    ebooks = EBook.objects.all().order_by('-id')

    # Search (only using fields that exist)
    search = request.GET.get('search', '')
    if search:
        ebooks = ebooks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    context = {
        'ebooks': ebooks,
        'search': search,
        'format_filter': '',  # Not used yet, but template expects it
    }

    return render(request, 'student_management/library/ebook_list.html', context)


@login_required
def ebook_form(request, pk=None):
    """Add or edit an e-book - UPDATED for minimal table structure"""
    if pk:
        ebook = get_object_or_404(EBook, pk=pk)
        title = "Edit E-Book"
    else:
        ebook = None
        title = "Upload E-Book"

    if request.method == 'POST':
        # Manual form processing for minimal fields
        title_field = request.POST.get('title')
        description_field = request.POST.get('description', '')
        file_field = request.FILES.get('file')

        if title_field and (file_field or ebook):
            if ebook:
                # Update existing
                ebook.title = title_field
                ebook.description = description_field
                if file_field:
                    ebook.file = file_field
                ebook.save()
            else:
                # Create new
                if file_field:
                    ebook = EBook.objects.create(
                        title=title_field,
                        description=description_field,
                        file=file_field
                    )
                else:
                    messages.error(request, 'Please select a file to upload.')
                    return redirect('ebook_form')

            messages.success(request, 'E-book saved successfully!')
            return redirect('ebook_list')
        else:
            messages.error(request, 'Please provide a title and file.')

    context = {
        'title': title,
        'object': ebook,
        'ebook': ebook,  # For template
    }

    return render(request, 'student_management/library/ebook_form_simple.html', context)


@login_required
def ebook_delete(request, pk):
    """Delete an e-book"""
    ebook = get_object_or_404(EBook, pk=pk)

    if request.method == 'POST':
        # Delete the file from storage
        if ebook.file:
            try:
                ebook.file.delete()
            except:
                pass

        ebook.delete()
        messages.success(request, 'E-book deleted successfully!')
        return redirect('ebook_list')

    context = {'ebook': ebook}
    return render(request, 'student_management/library/ebook_confirm_delete.html', context)


# ============================================================================
# ALSO UPDATE library_panel view - Use 'id' instead of date fields
# ============================================================================

@login_required
def library_panel(request):
    """Main library management panel with statistics"""

    # Get user's institution if applicable
    try:
        if hasattr(request.user, 'profile'):
            institution = request.user.profile.institution
        else:
            institution = None
    except:
        institution = None

    # Statistics
    try:
        total_books = Book.objects.count()
        available_books = Book.objects.filter(available_quantity__gt=0).count()
        total_members = LibraryMember.objects.count()
        active_issues = IssueReturn.objects.filter(status__in=['issued', 'overdue']).count()
        overdue_books = IssueReturn.objects.filter(status='overdue').count()
        total_ebooks = EBook.objects.count()
    except:
        total_books = 0
        available_books = 0
        total_members = 0
        active_issues = 0
        overdue_books = 0
        total_ebooks = 0

    # Get recent data for each tab
    try:
        books = Book.objects.all().order_by('-id')[:12]
    except:
        books = []

    try:
        members = LibraryMember.objects.select_related('student').all().order_by('-id')[:20]
    except:
        members = []

    try:
        issues = IssueReturn.objects.select_related('book', 'member__student').all().order_by('-id')[:20]  # Changed from '-issue_date'
    except:
        issues = []

    try:
        ebooks = EBook.objects.all().order_by('-id')[:12]  # Changed from '-uploaded_on'
    except:
        ebooks = []

    context = {
        # Statistics
        'total_books': total_books,
        'available_books': available_books,
        'total_members': total_members,
        'active_issues': active_issues,
        'overdue_books': overdue_books,
        'total_ebooks': total_ebooks,

        # Data for tabs
        'books': books,
        'members': members,
        'issues': issues,
        'ebooks': ebooks,
    }

    return render(request, 'student_management/library/panel.html', context)
