"""
Attendance URL Patterns

Add these to your student_management/urls.py
"""

from django.urls import path
from . import views

# Teacher Attendance URLs
path('teachers/attendance/', views.teacher_attendance_dashboard, name='teacher_attendance_dashboard'),
path('teachers/attendance/mark/', views.teacher_attendance_mark, name='teacher_attendance_mark'),

# Student Attendance URLs
path('student-attendance/select/', views.student_attendance_mark_select, name='student_attendance_mark_select'),
path('student-attendance/mark/', views.student_attendance_mark_dashboard, name='student_attendance_mark_dashboard'),
path('student-attendance/save/', views.student_attendance_save, name='student_attendance_save'),

# Attendance Reports
path('attendance/report/form/', views.attendance_report_form, name='attendance_report_form'),
