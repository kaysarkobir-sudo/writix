"""
Teacher Attendance Models

Add these to your student_management/models.py
"""

from django.db import models
from django.utils import timezone


class TeacherAttendance(models.Model):
    """Model for tracking teacher attendance"""

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('leave', 'On Leave'),
    ]

    teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present'
    )
    marked_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_teacher_attendance'
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    # Institution for multi-tenancy
    institution = models.ForeignKey(
        'Institution',
        on_delete=models.CASCADE,
        related_name='teacher_attendance_records',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Teacher Attendance'
        verbose_name_plural = 'Teacher Attendance Records'
        ordering = ['-date', 'teacher__last_name']
        unique_together = ['teacher', 'date']  # One attendance record per teacher per day
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['teacher', 'date']),
            models.Index(fields=['institution', 'date']),
        ]

    def __str__(self):
        return f"{self.teacher} - {self.date} - {self.get_status_display()}"


class StudentAttendance(models.Model):
    """Model for tracking student attendance"""

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('leave', 'On Leave'),
        ('excused', 'Excused Absence'),
    ]

    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present'
    )
    academic_class = models.ForeignKey(
        'AcademicClass',
        on_delete=models.CASCADE,
        related_name='student_attendance_records',
        null=True,
        blank=True
    )
    section = models.ForeignKey(
        'Section',
        on_delete=models.CASCADE,
        related_name='student_attendance_records',
        null=True,
        blank=True
    )
    session = models.ForeignKey(
        'AcademicYear',
        on_delete=models.CASCADE,
        related_name='student_attendance_records',
        null=True,
        blank=True
    )
    marked_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_student_attendance'
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    # Institution for multi-tenancy
    institution = models.ForeignKey(
        'Institution',
        on_delete=models.CASCADE,
        related_name='student_attendance_records',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Student Attendance'
        verbose_name_plural = 'Student Attendance Records'
        ordering = ['-date', 'student__last_name']
        unique_together = ['student', 'date']  # One attendance record per student per day
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['student', 'date']),
            models.Index(fields=['academic_class', 'date']),
            models.Index(fields=['institution', 'date']),
        ]

    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"
