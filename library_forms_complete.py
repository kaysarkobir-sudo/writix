"""
Library Management Forms
Add these to your student_management/forms.py (create if doesn't exist)

If you don't have a forms.py file, create it in your student_management app folder
"""

from django import forms
from .models import Book, LibraryMember, IssueReturn, EBook


class BookForm(forms.ModelForm):
    """Form for adding/editing books"""

    class Meta:
        model = Book
        fields = [
            'name', 'author', 'publisher', 'isbn', 'edition', 'publication_year',
            'category', 'subject_code', 'language', 'price', 'quantity',
            'available_quantity', 'rack_no', 'shelf_location', 'pages',
            'description', 'cover_image', 'barcode', 'date_added'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter book title'}),
            'author': forms.TextInput(attrs={'placeholder': 'Enter author name'}),
            'publisher': forms.TextInput(attrs={'placeholder': 'Enter publisher name'}),
            'isbn': forms.TextInput(attrs={'placeholder': 'Enter ISBN (13 digits)'}),
            'edition': forms.TextInput(attrs={'placeholder': 'e.g., 1st Edition, 2nd Edition'}),
            'publication_year': forms.NumberInput(attrs={'placeholder': 'e.g., 2024'}),
            'subject_code': forms.TextInput(attrs={'placeholder': 'e.g., CS101'}),
            'language': forms.TextInput(attrs={'placeholder': 'e.g., English, Bengali'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Enter price in BDT'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Total quantity'}),
            'available_quantity': forms.NumberInput(attrs={'placeholder': 'Available quantity'}),
            'rack_no': forms.TextInput(attrs={'placeholder': 'e.g., A1, B2'}),
            'shelf_location': forms.TextInput(attrs={'placeholder': 'e.g., Top shelf, Section A'}),
            'pages': forms.NumberInput(attrs={'placeholder': 'Number of pages'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief description of the book'}),
            'barcode': forms.TextInput(attrs={'placeholder': 'Enter barcode number'}),
            'date_added': forms.DateInput(attrs={'type': 'date'}),
        }


class LibraryMemberForm(forms.ModelForm):
    """Form for adding/editing library members"""

    class Meta:
        model = LibraryMember
        fields = [
            'student', 'library_id', 'joined_on', 'valid_until', 'status',
            'max_books_allowed', 'current_books_count', 'total_books_borrowed',
            'total_fines_paid', 'outstanding_fine', 'notes'
        ]
        widgets = {
            'library_id': forms.TextInput(attrs={'placeholder': 'e.g., LIB2024001'}),
            'joined_on': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'max_books_allowed': forms.NumberInput(attrs={'placeholder': 'Default: 3'}),
            'current_books_count': forms.NumberInput(attrs={'placeholder': 'Auto-updated'}),
            'total_books_borrowed': forms.NumberInput(attrs={'placeholder': 'Lifetime count'}),
            'total_fines_paid': forms.NumberInput(attrs={'placeholder': 'Total fines paid'}),
            'outstanding_fine': forms.NumberInput(attrs={'placeholder': 'Current unpaid fines'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes about this member'}),
        }


class IssueReturnForm(forms.ModelForm):
    """Form for issuing/returning books"""

    class Meta:
        model = IssueReturn
        fields = [
            'member', 'book', 'issue_date', 'due_date', 'expected_return_date',
            'return_date', 'actual_return_date', 'status', 'condition_at_issue',
            'condition_at_return', 'fine_amount', 'fine_paid', 'fine_per_day',
            'remarks'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_return_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
            'actual_return_date': forms.DateInput(attrs={'type': 'date'}),
            'condition_at_issue': forms.TextInput(attrs={'placeholder': 'e.g., Good, Fair, Excellent'}),
            'condition_at_return': forms.TextInput(attrs={'placeholder': 'e.g., Good, Damaged'}),
            'fine_amount': forms.NumberInput(attrs={'placeholder': 'Fine amount in BDT'}),
            'fine_per_day': forms.NumberInput(attrs={'placeholder': 'Default: 5.00 BDT'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any additional notes'}),
        }


class EBookForm(forms.ModelForm):
    """Form for uploading/editing e-books"""

    class Meta:
        model = EBook
        fields = [
            'title', 'author', 'file', 'cover_image', 'description',
            'category', 'format', 'file_size', 'pages', 'is_public'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter e-book title'}),
            'author': forms.TextInput(attrs={'placeholder': 'Enter author name'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Brief description or summary'}),
            'category': forms.TextInput(attrs={'placeholder': 'e.g., Fiction, Science, History'}),
            'file_size': forms.TextInput(attrs={'placeholder': 'e.g., 5.2 MB, 12 KB'}),
            'pages': forms.NumberInput(attrs={'placeholder': 'Number of pages'}),
        }
