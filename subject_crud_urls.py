"""
URL Patterns for Subject CRUD

Add these to your student_management/urls.py
"""

# Subject CRUD Management
path('academic/subjects/', views.subject_list, name='subject_list'),
path('academic/subjects/create/', views.subject_create, name='subject_create'),
path('academic/subjects/<int:pk>/update/', views.subject_update, name='subject_update'),
path('academic/subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
