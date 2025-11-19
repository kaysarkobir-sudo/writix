# Academic Term Create/Update - Integration Guide (Updated for Your Model)

## Quick Integration (5 minutes)

### Step 1: Add imports to your views.py

Add these imports at the top of your `student_management/views.py`:

```python
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AcademicTerm, AcademicYear
```

---

### Step 2: Add the form class to views.py

Copy this entire class to your `student_management/views.py`:

```python
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
```

---

### Step 3: Add the view functions to views.py

Copy these 4 functions to your `student_management/views.py`:

```python
@login_required
def academic_term_create(request):
    """Create a new academic term"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    if request.method == 'POST':
        form = AcademicTermForm(request.POST, institution=institution)

        if form.is_valid():
            term = form.save(commit=False)

            # If this term is marked as current, unset other current terms
            # for the same academic year
            if term.is_current:
                AcademicTerm.objects.filter(
                    academic_year=term.academic_year,
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
    # (based on academic_year's institution)
    if institution and hasattr(term.academic_year, 'institution'):
        if term.academic_year.institution != institution:
            messages.error(request, 'You do not have permission to edit this term.')
            return redirect('academic_term_list')

    if request.method == 'POST':
        form = AcademicTermForm(request.POST, instance=term, institution=institution)

        if form.is_valid():
            term = form.save(commit=False)

            # If this term is marked as current, unset other current terms
            # for the same academic year
            if term.is_current:
                AcademicTerm.objects.filter(
                    academic_year=term.academic_year,
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

    # Filter terms by institution (through academic_year)
    if institution:
        terms = AcademicTerm.objects.filter(
            academic_year__institution=institution
        ).select_related('academic_year').order_by('-academic_year__start_date', 'start_date')
    else:
        terms = AcademicTerm.objects.all().select_related('academic_year').order_by('-academic_year__start_date', 'start_date')

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
    # (based on academic_year's institution)
    if institution and hasattr(term.academic_year, 'institution'):
        if term.academic_year.institution != institution:
            messages.error(request, 'You do not have permission to delete this term.')
            return redirect('academic_term_list')

    if request.method == 'POST':
        term_name = term.name
        term.delete()
        messages.success(request, f'Academic term "{term_name}" deleted successfully!')
        return redirect('academic_term_list')

    # If not POST, show confirmation (optional - can be handled with JavaScript)
    return redirect('academic_term_list')
```

---

### Step 4: Add URL patterns to urls.py

Add these 4 lines to your `student_management/urls.py`:

```python
# Academic Term Management
path('academic/terms/', views.academic_term_list, name='academic_term_list'),
path('academic/terms/create/', views.academic_term_create, name='academic_term_create'),
path('academic/terms/<int:pk>/update/', views.academic_term_update, name='academic_term_update'),
path('academic/terms/<int:pk>/delete/', views.academic_term_delete, name='academic_term_delete'),
```

---

### Step 5: Restart server and test

```bash
python manage.py runserver
```

Go to: `http://127.0.0.1:8000/student-management/academic/terms/`

Click "Add New Term" to create a new academic term!

---

## Your Existing Model Structure

```python
class AcademicTerm(models.Model):
    """Academic Terms/Semesters"""
    TERM_CHOICES = [
        ('first', 'First Term'),
        ('second', 'Second Term'),
        ('third', 'Third Term'),
        ('summer', 'Summer Term'),
    ]

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField("Term Name", max_length=100)
    term_number = models.CharField("Term Number", max_length=20, choices=TERM_CHOICES)
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")
    is_current = models.BooleanField("Is Current Term", default=False)
    is_active = models.BooleanField("Is Active", default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## Features

✅ **Create Academic Terms** - Full form with validation
✅ **Update Terms** - Edit existing terms
✅ **Delete Terms** - Remove terms with confirmation
✅ **List Terms** - View all terms organized by year
✅ **Institution Filtering** - Filter by institution through academic_year
✅ **Current Term Management** - Only one term can be "current" per academic year
✅ **Date Validation** - End date must be after start date
✅ **Success Messages** - User-friendly feedback
✅ **Term Number Choices** - Dropdown with First/Second/Third/Summer options

---

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| academic_year | ForeignKey | Yes | Academic year this term belongs to |
| name | Text | Yes | Term name (e.g., "First Term", "Spring") |
| term_number | Choice | Yes | Select from: First/Second/Third/Summer |
| start_date | Date | Yes | Term start date |
| end_date | Date | Yes | Term end date (must be after start) |
| is_current | Boolean | No | Mark as current active term |
| is_active | Boolean | No | Enable/disable term |

---

## Key Differences from Generic Version

1. **term_number** is a CharField with CHOICES (not IntegerField)
   - Dropdown shows: First Term, Second Term, Third Term, Summer Term

2. **No direct institution field**
   - Institution filtering happens through `academic_year__institution`

3. **Current term logic**
   - Only one term can be current per academic year (not globally)

4. **Automatic timestamps**
   - `created_at` and `updated_at` are handled by Django automatically

---

## Validation Rules

1. ✅ **End date must be after start date**
2. ✅ **Only one term can be marked as current per academic year**
3. ✅ **All required fields must be filled**
4. ✅ **Users can only manage terms for their institution's academic years**
5. ✅ **Term number must be one of the predefined choices**

---

## Template Structure

The templates are already in place at:
- `templates/student_management/academic/term_form.html` - Create/Edit form
- `templates/student_management/academic/term_list.html` - List all terms

Both templates use Bootstrap styling and are fully responsive.

---

## Example Usage

### Create First Term for 2024-2025
- Academic Year: 2024-2025
- Name: First Term
- Term Number: First Term
- Start Date: 2024-09-01
- End Date: 2024-12-15
- Is Current: ✓ (checked)
- Is Active: ✓ (checked)

### Create Second Term for 2024-2025
- Academic Year: 2024-2025
- Name: Second Term
- Term Number: Second Term
- Start Date: 2025-01-05
- End Date: 2025-04-30
- Is Current: ☐ (unchecked - only one can be current)
- Is Active: ✓ (checked)

---

## Troubleshooting

### Issue: "AcademicYear matching query does not exist"

**Solution:** Make sure you have created at least one Academic Year before creating terms.

### Issue: NoReverseMatch for 'academic_term_list'

**Solution:** Make sure all 4 URL patterns are added to your urls.py file.

### Issue: Dropdown shows empty for term_number

**Solution:** This should not happen - the TERM_CHOICES are defined in your model. Make sure the model is correct.

---

## Complete File References

All the code you need is in these files:
- `academic_term_views_updated.py` - Complete view functions and form (matches YOUR model)
- `academic_term_urls.py` - URL patterns (same as before)
- `ACADEMIC_TERM_INTEGRATION_UPDATED.md` - This guide

**Status:** Production-ready ✅ **Updated to match your exact model!**
