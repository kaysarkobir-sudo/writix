"""
Library Management URL Patterns
Add these to your student_management/urls.py or main urls.py

Location: student_management/urls.py
"""

from django.urls import path
from . import views

# Add these to your existing urlpatterns list:

urlpatterns = [
    # ... your existing URL patterns ...

    # ===== LIBRARY MANAGEMENT URLS =====

    # Main Library Panel
    path('library/', views.library_panel, name='library_panel'),

    # Book Management
    path('library/books/', views.book_list, name='book_list'),
    path('library/books/add/', views.book_form, name='book_form'),
    path('library/books/<int:pk>/edit/', views.book_form, name='book_form'),
    path('library/books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Library Member Management
    path('library/members/', views.library_member_list, name='library_member_list'),
    path('library/members/add/', views.library_member_form, name='library_member_form'),
    path('library/members/<int:pk>/edit/', views.library_member_form, name='library_member_form'),
    path('library/members/<int:pk>/delete/', views.library_member_delete, name='library_member_delete'),

    # Issue/Return Management
    path('library/issues/', views.issue_return_list, name='issue_return_list'),
    path('library/issues/add/', views.issue_return_form, name='issue_return_form'),
    path('library/issues/<int:pk>/return/', views.issue_return_form, name='issue_return_form'),
    path('library/issues/<int:pk>/delete/', views.issue_return_delete, name='issue_return_delete'),

    # E-Book Management
    path('library/ebooks/', views.ebook_list, name='ebook_list'),
    path('library/ebooks/add/', views.ebook_form, name='ebook_form'),
    path('library/ebooks/<int:pk>/edit/', views.ebook_form, name='ebook_form'),
    path('library/ebooks/<int:pk>/delete/', views.ebook_delete, name='ebook_delete'),
]


# ===== ALTERNATIVE: If using app_name namespace =====
# If your student_management/urls.py has app_name = 'student_management'
# Then your templates should use {% url 'student_management:library_panel' %}
# instead of {% url 'library_panel' %}

# Example:
"""
app_name = 'student_management'

urlpatterns = [
    # ... existing patterns ...
    path('library/', views.library_panel, name='library_panel'),
    # ... rest of library URLs ...
]
"""
