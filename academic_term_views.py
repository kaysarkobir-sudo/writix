"""
Academic Term Create/Update Views and Forms
Add these to your student_management app
"""

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AcademicTerm, AcademicYear


# ============================================
# FORM
# ============================================

class AcademicTermForm(forms.ModelForm):
    """Form for creating and editing academic terms"""

    class Meta:
        model = AcademicTerm
        fields = [
            'academic_year',
            'name',
            'term_number',
            'start_date',
            'end_date',
            'is_current',
            'is_active',
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        institution = kwargs.pop('institution', None)
        super().__init__(*args, **kwargs)

        # Filter academic years by institution if provided
        if institution:
            self.fields['academic_year'].queryset = AcademicYear.objects.filter(
                institution=institution
            )

        # Add placeholders and help text
        self.fields['name'].widget.attrs.update({
            'placeholder': 'e.g., First Term, Spring Semester'
        })
        self.fields['term_number'].widget.attrs.update({
            'placeholder': '1, 2, 3, etc.'
        })

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validate that end_date is after start_date
        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError({
                    'end_date': 'End date must be after start date.'
                })

        return cleaned_data


# ============================================
# VIEWS
# ============================================

@login_required
def academic_term_create(request):
    """Create a new academic term"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    if request.method == 'POST':
        form = AcademicTermForm(request.POST, institution=institution)

        if form.is_valid():
            term = form.save(commit=False)

            # Set institution if available
            if institution:
                term.institution = institution

            # If this term is marked as current, unset other current terms
            if term.is_current:
                AcademicTerm.objects.filter(
                    institution=institution,
                    is_current=True
                ).update(is_current=False)

            term.save()

            messages.success(request, f'Academic term "{term.name}" created successfully!')
            return redirect('academic_term_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AcademicTermForm(institution=institution)

    context = {
        'form': form,
        'title': 'Add New Academic Term',
    }

    return render(request, 'student_management/academic/term_form.html', context)


@login_required
def academic_term_update(request, pk):
    """Update an existing academic term"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    # Get the term
    term = get_object_or_404(AcademicTerm, pk=pk)

    # Check if user has permission to edit this term
    if institution and term.institution != institution:
        messages.error(request, 'You do not have permission to edit this term.')
        return redirect('academic_term_list')

    if request.method == 'POST':
        form = AcademicTermForm(request.POST, instance=term, institution=institution)

        if form.is_valid():
            term = form.save(commit=False)

            # If this term is marked as current, unset other current terms
            if term.is_current:
                AcademicTerm.objects.filter(
                    institution=institution,
                    is_current=True
                ).exclude(pk=term.pk).update(is_current=False)

            term.save()

            messages.success(request, f'Academic term "{term.name}" updated successfully!')
            return redirect('academic_term_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AcademicTermForm(instance=term, institution=institution)

    context = {
        'form': form,
        'title': 'Edit Academic Term',
    }

    return render(request, 'student_management/academic/term_form.html', context)


@login_required
def academic_term_list(request):
    """List all academic terms"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    # Filter terms by institution
    if institution:
        terms = AcademicTerm.objects.filter(institution=institution).select_related('academic_year').order_by('-academic_year', 'term_number')
    else:
        terms = AcademicTerm.objects.all().select_related('academic_year').order_by('-academic_year', 'term_number')

    context = {
        'terms': terms,
    }

    return render(request, 'student_management/academic/term_list.html', context)


@login_required
def academic_term_delete(request, pk):
    """Delete an academic term"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    # Get the term
    term = get_object_or_404(AcademicTerm, pk=pk)

    # Check if user has permission to delete this term
    if institution and term.institution != institution:
        messages.error(request, 'You do not have permission to delete this term.')
        return redirect('academic_term_list')

    if request.method == 'POST':
        term_name = term.name
        term.delete()
        messages.success(request, f'Academic term "{term_name}" deleted successfully!')
        return redirect('academic_term_list')

    # If not POST, show confirmation (optional - can be handled with JavaScript)
    return redirect('academic_term_list')
