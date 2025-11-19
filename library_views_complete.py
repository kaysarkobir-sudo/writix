"""
Library Management View Functions
Add these to your student_management/views.py

Copy and paste all these functions into your views.py file
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Book, LibraryMember, IssueReturn, EBook, Student
from .forms import (
    BookForm, LibraryMemberForm, IssueReturnForm, EBookForm
)  # You'll need to create these forms


# ============================================================================
# LIBRARY PANEL (Main Dashboard)
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
        issues = IssueReturn.objects.select_related('book', 'member__student').all().order_by('-issue_date')[:20]
    except:
        issues = []

    try:
        ebooks = EBook.objects.all().order_by('-uploaded_on')[:12]
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


# ============================================================================
# BOOK MANAGEMENT
# ============================================================================

@login_required
def book_list(request):
    """List all books"""
    books = Book.objects.all().order_by('name')

    # Search functionality
    search = request.GET.get('search', '')
    if search:
        books = books.filter(
            Q(name__icontains=search) |
            Q(author__icontains=search) |
            Q(isbn__icontains=search) |
            Q(category__icontains=search)
        )

    context = {
        'books': books,
        'search': search,
    }

    return render(request, 'student_management/library/book_list.html', context)


@login_required
def book_form(request, pk=None):
    """Add or edit a book"""
    if pk:
        book = get_object_or_404(Book, pk=pk)
        title = "Edit Book"
    else:
        book = None
        title = "Add New Book"

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book saved successfully!')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)

    context = {
        'form': form,
        'title': title,
        'object': book,
    }

    return render(request, 'student_management/library/book_form.html', context)


@login_required
def book_delete(request, pk):
    """Delete a book"""
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')

    return render(request, 'student_management/library/book_confirm_delete.html', {'book': book})


# ============================================================================
# LIBRARY MEMBER MANAGEMENT
# ============================================================================

@login_required
def library_member_list(request):
    """List all library members"""
    members = LibraryMember.objects.select_related('student').all().order_by('-joined_on')

    # Search functionality
    search = request.GET.get('search', '')
    if search:
        members = members.filter(
            Q(library_id__icontains=search) |
            Q(student__first_name__icontains=search) |
            Q(student__last_name__icontains=search)
        )

    context = {
        'members': members,
        'search': search,
    }

    return render(request, 'student_management/library/member_list.html', context)


@login_required
def library_member_form(request, pk=None):
    """Add or edit a library member"""
    if pk:
        member = get_object_or_404(LibraryMember, pk=pk)
        title = "Edit Library Member"
    else:
        member = None
        title = "Add New Library Member"

    if request.method == 'POST':
        form = LibraryMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Library member saved successfully!')
            return redirect('library_member_list')
    else:
        form = LibraryMemberForm(instance=member)

    context = {
        'form': form,
        'title': title,
        'object': member,
    }

    return render(request, 'student_management/library/member_form.html', context)


@login_required
def library_member_delete(request, pk):
    """Delete a library member"""
    member = get_object_or_404(LibraryMember, pk=pk)

    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Library member deleted successfully!')
        return redirect('library_member_list')

    return render(request, 'student_management/library/member_confirm_delete.html', {'member': member})


# ============================================================================
# ISSUE/RETURN MANAGEMENT
# ============================================================================

@login_required
def issue_return_list(request):
    """List all issue/return records"""
    issues = IssueReturn.objects.select_related(
        'book', 'member__student'
    ).all().order_by('-issue_date')

    # Search and filter
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    if search:
        issues = issues.filter(
            Q(book__name__icontains=search) |
            Q(member__student__first_name__icontains=search) |
            Q(member__student__last_name__icontains=search) |
            Q(member__library_id__icontains=search)
        )

    if status:
        issues = issues.filter(status=status)

    context = {
        'issues': issues,
        'search': search,
        'status': status,
    }

    return render(request, 'student_management/library/issue_list.html', context)


@login_required
def issue_return_form(request, pk=None):
    """Issue a book or process return"""
    if pk:
        issue = get_object_or_404(IssueReturn, pk=pk)
        title = "Process Return"
    else:
        issue = None
        title = "Issue Book"

    if request.method == 'POST':
        form = IssueReturnForm(request.POST, instance=issue)
        if form.is_valid():
            issue_obj = form.save(commit=False)

            # Set issued_by on new issue
            if not pk:
                issue_obj.issued_by = request.user

            # Set returned_to on return
            if issue_obj.return_date and not issue_obj.returned_to:
                issue_obj.returned_to = request.user

            issue_obj.save()

            # Update book availability
            book = issue_obj.book
            if not pk:  # New issue
                book.available_quantity -= 1
                book.save()
            elif issue_obj.status == 'returned':  # Return
                book.available_quantity += 1
                book.save()

            # Update member's current books count
            member = issue_obj.member
            if not pk:  # New issue
                member.current_books_count += 1
                member.total_books_borrowed += 1
                member.save()
            elif issue_obj.status == 'returned':  # Return
                member.current_books_count -= 1
                if issue_obj.fine_amount > 0 and not issue_obj.fine_paid:
                    member.outstanding_fine += issue_obj.fine_amount
                member.save()

            messages.success(request, 'Transaction completed successfully!')
            return redirect('issue_return_list')
    else:
        form = IssueReturnForm(instance=issue)

    context = {
        'form': form,
        'title': title,
        'object': issue,
    }

    return render(request, 'student_management/library/issue_form.html', context)


@login_required
def issue_return_delete(request, pk):
    """Delete an issue/return record"""
    issue = get_object_or_404(IssueReturn, pk=pk)

    if request.method == 'POST':
        issue.delete()
        messages.success(request, 'Record deleted successfully!')
        return redirect('issue_return_list')

    return render(request, 'student_management/library/issue_confirm_delete.html', {'issue': issue})


# ============================================================================
# E-BOOK MANAGEMENT
# ============================================================================

@login_required
def ebook_list(request):
    """List all e-books"""
    ebooks = EBook.objects.all().order_by('-uploaded_on')

    # Search and filter
    search = request.GET.get('search', '')
    format_filter = request.GET.get('format', '')

    if search:
        ebooks = ebooks.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(category__icontains=search)
        )

    if format_filter:
        ebooks = ebooks.filter(format=format_filter)

    context = {
        'ebooks': ebooks,
        'search': search,
        'format_filter': format_filter,
    }

    return render(request, 'student_management/library/ebook_list.html', context)


@login_required
def ebook_form(request, pk=None):
    """Add or edit an e-book"""
    if pk:
        ebook = get_object_or_404(EBook, pk=pk)
        title = "Edit E-Book"
    else:
        ebook = None
        title = "Upload E-Book"

    if request.method == 'POST':
        form = EBookForm(request.POST, request.FILES, instance=ebook)
        if form.is_valid():
            ebook_obj = form.save(commit=False)

            # Set uploaded_by on new upload
            if not pk:
                ebook_obj.uploaded_by = request.user

            ebook_obj.save()
            messages.success(request, 'E-book saved successfully!')
            return redirect('ebook_list')
    else:
        form = EBookForm(instance=ebook)

    context = {
        'form': form,
        'title': title,
        'object': ebook,
    }

    return render(request, 'student_management/library/ebook_form.html', context)


@login_required
def ebook_delete(request, pk):
    """Delete an e-book"""
    ebook = get_object_or_404(EBook, pk=pk)

    if request.method == 'POST':
        # Delete the file from storage
        if ebook.file:
            ebook.file.delete()
        if ebook.cover_image:
            ebook.cover_image.delete()

        ebook.delete()
        messages.success(request, 'E-book deleted successfully!')
        return redirect('ebook_list')

    return render(request, 'student_management/library/ebook_confirm_delete.html', {'ebook': ebook})
