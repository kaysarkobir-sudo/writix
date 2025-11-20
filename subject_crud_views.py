"""
Subject CRUD Views and Forms
For managing school subjects with create/update/delete/list functionality

Add these to your student_management/views.py
"""

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Subject, Department, AcademicClass


# ============================================
# FORM
# ============================================

class SubjectForm(forms.ModelForm):
    """Form for creating and editing subjects"""

    class Meta:
        model = Subject
        fields = [
            'name',
            'code',
            'subject_type',
            'student_class',
            'department',
            'author',
            'description',
            'note',
            'is_active',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        institution = kwargs.pop('institution', None)
        super().__init__(*args, **kwargs)

        # Filter departments and classes by institution if provided
        if institution:
            self.fields['department'].queryset = Department.objects.filter(
                institution=institution
            )
            self.fields['student_class'].queryset = AcademicClass.objects.filter(
                institution=institution
            )

        # Add placeholders and help text
        self.fields['name'].widget.attrs.update({
            'placeholder': 'e.g., Mathematics, English, Physics'
        })
        self.fields['code'].widget.attrs.update({
            'placeholder': 'e.g., MATH101, ENG101'
        })
        self.fields['author'].widget.attrs.update({
            'placeholder': 'Subject author or creator (optional)'
        })

        # Make department optional in the form
        self.fields['department'].required = False

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        code = cleaned_data.get('code')

        # Sync subject_name with name and subject_code with code
        if name:
            cleaned_data['subject_name'] = name
        if code:
            cleaned_data['subject_code'] = code

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Ensure subject_name and subject_code are synced with name and code
        instance.subject_name = instance.name
        instance.subject_code = instance.code

        if commit:
            instance.save()
        return instance


# ============================================
# VIEWS
# ============================================

@login_required
def subject_create(request):
    """Create a new subject"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    if request.method == 'POST':
        form = SubjectForm(request.POST, institution=institution)

        if form.is_valid():
            subject = form.save(commit=False)

            # Set institution
            if institution:
                subject.institution = institution

            # Check if subject with same name or code already exists
            existing_name = Subject.objects.filter(
                institution=institution,
                name=subject.name
            ).exists()

            existing_code = Subject.objects.filter(
                institution=institution,
                code=subject.code
            ).exists()

            if existing_name:
                messages.error(request, f'A subject with the name "{subject.name}" already exists.')
                context = {
                    'form': form,
                    'title': 'Add New Subject',
                }
                return render(request, 'student_management/academic/subject_form_updated.html', context)

            if existing_code:
                messages.error(request, f'A subject with the code "{subject.code}" already exists.')
                context = {
                    'form': form,
                    'title': 'Add New Subject',
                }
                return render(request, 'student_management/academic/subject_form_updated.html', context)

            subject.save()

            messages.success(request, f'Subject "{subject.name}" created successfully!')
            return redirect('subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(institution=institution)

    context = {
        'form': form,
        'title': 'Add New Subject',
    }

    return render(request, 'student_management/academic/subject_form_updated.html', context)


@login_required
def subject_update(request, pk):
    """Update an existing subject"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    # Get the subject
    subject = get_object_or_404(Subject, pk=pk)

    # Check if user has permission to edit this subject
    if institution and subject.institution != institution:
        messages.error(request, 'You do not have permission to edit this subject.')
        return redirect('subject_list')

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject, institution=institution)

        if form.is_valid():
            subject = form.save(commit=False)

            # Check if subject with same name already exists (excluding current)
            existing_name = Subject.objects.filter(
                institution=institution,
                name=subject.name
            ).exclude(pk=subject.pk).exists()

            existing_code = Subject.objects.filter(
                institution=institution,
                code=subject.code
            ).exclude(pk=subject.pk).exists()

            if existing_name:
                messages.error(request, f'A subject with the name "{subject.name}" already exists.')
                context = {
                    'form': form,
                    'title': 'Edit Subject',
                }
                return render(request, 'student_management/academic/subject_form_updated.html', context)

            if existing_code:
                messages.error(request, f'A subject with the code "{subject.code}" already exists.')
                context = {
                    'form': form,
                    'title': 'Edit Subject',
                }
                return render(request, 'student_management/academic/subject_form_updated.html', context)

            subject.save()

            messages.success(request, f'Subject "{subject.name}" updated successfully!')
            return redirect('subject_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(instance=subject, institution=institution)

    context = {
        'form': form,
        'title': 'Edit Subject',
    }

    return render(request, 'student_management/academic/subject_form_updated.html', context)


@login_required
def subject_list(request):
    """List all subjects"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    # Filter subjects by institution
    if institution:
        subjects = Subject.objects.filter(
            institution=institution
        ).select_related('department', 'student_class').order_by('student_class__name', 'name')
    else:
        subjects = Subject.objects.all().select_related('department', 'student_class').order_by('student_class__name', 'name')

    context = {
        'subjects': subjects,
    }

    return render(request, 'student_management/academic/subject_list_updated.html', context)


@login_required
def subject_delete(request, pk):
    """Delete a subject"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    # Get the subject
    subject = get_object_or_404(Subject, pk=pk)

    # Check if user has permission to delete this subject
    if institution and subject.institution != institution:
        messages.error(request, 'You do not have permission to delete this subject.')
        return redirect('subject_list')

    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{subject_name}" deleted successfully!')
        return redirect('subject_list')

    # If not POST, show confirmation (optional - can be handled with JavaScript)
    return redirect('subject_list')
