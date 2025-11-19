"""
Academic Term URL Patterns
Add these to your student_management/urls.py
"""

from django.urls import path
from . import views

# Academic Term URLs
urlpatterns = [
    # Academic Term Management
    path('academic/terms/', views.academic_term_list, name='academic_term_list'),
    path('academic/terms/create/', views.academic_term_create, name='academic_term_create'),
    path('academic/terms/<int:pk>/update/', views.academic_term_update, name='academic_term_update'),
    path('academic/terms/<int:pk>/delete/', views.academic_term_delete, name='academic_term_delete'),
]

# ============================================
# INSTALLATION INSTRUCTIONS
# ============================================

"""
STEP 1: Add the view functions to your views.py

Copy the following functions from academic_term_views.py to your student_management/views.py:
1. AcademicTermForm (class)
2. academic_term_create (function)
3. academic_term_update (function)
4. academic_term_list (function)
5. academic_term_delete (function)


STEP 2: Add the URL patterns to your urls.py

Add these URL patterns to your student_management/urls.py:

    path('academic/terms/', views.academic_term_list, name='academic_term_list'),
    path('academic/terms/create/', views.academic_term_create, name='academic_term_create'),
    path('academic/terms/<int:pk>/update/', views.academic_term_update, name='academic_term_update'),
    path('academic/terms/<int:pk>/delete/', views.academic_term_delete, name='academic_term_delete'),


STEP 3: Make sure you have the required imports in views.py

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import AcademicTerm, AcademicYear


STEP 4: Verify your models

Make sure your models.py has AcademicTerm and AcademicYear models with these fields:

AcademicTerm:
- institution (ForeignKey to Institution)
- academic_year (ForeignKey to AcademicYear)
- name (CharField)
- term_number (IntegerField)
- start_date (DateField)
- end_date (DateField)
- is_current (BooleanField)
- is_active (BooleanField)


STEP 5: The templates already exist!

The templates are already in place:
- templates/student_management/academic/term_form.html
- templates/student_management/academic/term_list.html


STEP 6: Test the functionality

1. Go to: http://127.0.0.1:8000/student-management/academic/terms/
2. Click "Add New Term" button
3. Fill in the form and submit
4. You should see the new term in the list!


FEATURES:
- Create new academic terms
- Update existing terms
- Delete terms
- List all terms with filtering by institution
- Automatic validation (end date after start date)
- Only one term can be marked as "current" at a time
- Institution-based access control
"""
