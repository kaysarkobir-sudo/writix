"""
Attendance Views and Forms

Add these to your student_management/views.py
"""

import json
from datetime import date, datetime
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from .models import (
    Teacher, Student, TeacherAttendance, StudentAttendance,
    AcademicClass, Section, AcademicYear
)


# ============================================
# TEACHER ATTENDANCE
# ============================================

@login_required
def teacher_attendance_dashboard(request):
    """Display teacher attendance dashboard"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    # Get all teachers
    if institution:
        teachers = Teacher.objects.filter(
            institution=institution,
            is_active=True
        ).select_related('department').order_by('last_name', 'first_name')
    else:
        teachers = Teacher.objects.filter(is_active=True).select_related('department').order_by('last_name', 'first_name')

    context = {
        'teachers': teachers,
    }

    return render(request, 'student_management/teachers/attendance_dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def teacher_attendance_mark(request):
    """Handle teacher attendance marking (AJAX endpoint)"""

    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        attendance_date = data.get('date')
        attendance_records = data.get('attendance', {})

        # Validate date
        if not attendance_date:
            return JsonResponse({'success': False, 'error': 'Date is required'}, status=400)

        # Parse date
        try:
            attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)

        # Validate attendance records
        if not attendance_records:
            return JsonResponse({'success': False, 'error': 'No attendance records provided'}, status=400)

        # Get user's institution
        institution = getattr(request.user, 'institution', None)

        # Process each teacher's attendance
        saved_count = 0
        errors = []

        for teacher_id, status in attendance_records.items():
            try:
                # Get teacher
                teacher = Teacher.objects.get(id=teacher_id)

                # Check institution access
                if institution and teacher.institution != institution:
                    errors.append(f"Teacher {teacher_id}: Access denied")
                    continue

                # Create or update attendance record
                attendance, created = TeacherAttendance.objects.update_or_create(
                    teacher=teacher,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'marked_by': request.user,
                        'institution': institution if institution else teacher.institution,
                    }
                )

                saved_count += 1

            except Teacher.DoesNotExist:
                errors.append(f"Teacher {teacher_id}: Not found")
                continue
            except Exception as e:
                errors.append(f"Teacher {teacher_id}: {str(e)}")
                continue

        if saved_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'Successfully saved {saved_count} attendance records',
                'saved_count': saved_count,
                'errors': errors if errors else None
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No attendance records were saved',
                'errors': errors
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# STUDENT ATTENDANCE
# ============================================

class StudentAttendanceForm(forms.Form):
    """Form for selecting class and session for student attendance"""

    academic_class = forms.ModelChoiceField(
        queryset=AcademicClass.objects.all(),
        required=True,
        label='Class',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        required=False,
        label='Section (Optional)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    session = forms.ModelChoiceField(
        queryset=AcademicYear.objects.all(),
        required=True,
        label='Academic Session',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    attendance_date = forms.DateField(
        required=False,
        label='Date',
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )

    def __init__(self, *args, **kwargs):
        institution = kwargs.pop('institution', None)
        super().__init__(*args, **kwargs)

        # Filter by institution if provided
        if institution:
            self.fields['academic_class'].queryset = AcademicClass.objects.filter(
                institution=institution
            ).order_by('name')
            self.fields['section'].queryset = Section.objects.filter(
                academic_class__institution=institution
            ).order_by('name')
            self.fields['session'].queryset = AcademicYear.objects.filter(
                institution=institution
            ).order_by('-start_date')


@login_required
def student_attendance_mark_select(request):
    """Select class and session for marking student attendance"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    if request.method == 'POST':
        form = StudentAttendanceForm(request.POST, institution=institution)

        if form.is_valid():
            academic_class = form.cleaned_data['academic_class']
            section = form.cleaned_data.get('section')
            session = form.cleaned_data['session']
            attendance_date = form.cleaned_data.get('attendance_date') or date.today()

            # Redirect to marking page with parameters
            params = f"?class={academic_class.id}&session={session.id}&date={attendance_date}"
            if section:
                params += f"&section={section.id}"

            return redirect(f"/student-attendance/mark/{params}")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentAttendanceForm(institution=institution)

    context = {
        'form': form,
        'title': 'Mark Attendance'
    }

    return render(request, 'student_management/attendance/mark_select.html', context)


@login_required
def student_attendance_mark_dashboard(request):
    """Display student attendance marking dashboard"""

    # Get parameters from URL
    class_id = request.GET.get('class')
    section_id = request.GET.get('section')
    session_id = request.GET.get('session')
    attendance_date = request.GET.get('date', str(date.today()))

    if not class_id or not session_id:
        messages.error(request, 'Class and session are required')
        return redirect('student_attendance_mark_select')

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    try:
        # Get class and session
        academic_class = AcademicClass.objects.get(id=class_id)
        session = AcademicYear.objects.get(id=session_id)

        # Check institution access
        if institution and academic_class.institution != institution:
            messages.error(request, 'Access denied')
            return redirect('student_attendance_mark_select')

        # Get students
        students_query = Student.objects.filter(
            student_class=academic_class,
            is_active=True
        )

        if section_id:
            section = Section.objects.get(id=section_id)
            students_query = students_query.filter(section=section)
        else:
            section = None

        students = students_query.select_related('section').order_by('last_name', 'first_name')

        # Parse date
        try:
            attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            attendance_date_obj = date.today()

        # Get existing attendance for this date
        existing_attendance = {}
        if students:
            existing_records = StudentAttendance.objects.filter(
                student__in=students,
                date=attendance_date_obj
            )
            for record in existing_records:
                existing_attendance[record.student.id] = record.status

        context = {
            'students': students,
            'academic_class': academic_class,
            'section': section,
            'session': session,
            'attendance_date': attendance_date_obj,
            'existing_attendance': existing_attendance,
        }

        return render(request, 'student_management/attendance/mark_dashboard.html', context)

    except (AcademicClass.DoesNotExist, AcademicYear.DoesNotExist, Section.DoesNotExist):
        messages.error(request, 'Invalid class, section, or session')
        return redirect('student_attendance_mark_select')


@login_required
@require_http_methods(["POST"])
def student_attendance_save(request):
    """Handle student attendance saving (AJAX endpoint)"""

    try:
        # Parse JSON data from request
        data = json.loads(request.body)
        attendance_date = data.get('date')
        attendance_records = data.get('attendance', {})
        class_id = data.get('class_id')
        session_id = data.get('session_id')
        section_id = data.get('section_id')

        # Validate required fields
        if not attendance_date or not class_id or not session_id:
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

        # Parse date
        try:
            attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid date format'}, status=400)

        # Validate attendance records
        if not attendance_records:
            return JsonResponse({'success': False, 'error': 'No attendance records provided'}, status=400)

        # Get user's institution
        institution = getattr(request.user, 'institution', None)

        # Get class and session
        try:
            academic_class = AcademicClass.objects.get(id=class_id)
            session = AcademicYear.objects.get(id=session_id)
            section = Section.objects.get(id=section_id) if section_id else None

            # Check institution access
            if institution and academic_class.institution != institution:
                return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)

        except (AcademicClass.DoesNotExist, AcademicYear.DoesNotExist, Section.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Invalid class, session, or section'}, status=400)

        # Process each student's attendance
        saved_count = 0
        errors = []

        for student_id, status in attendance_records.items():
            try:
                # Get student
                student = Student.objects.get(id=student_id)

                # Check institution access
                if institution and student.institution != institution:
                    errors.append(f"Student {student_id}: Access denied")
                    continue

                # Create or update attendance record
                attendance, created = StudentAttendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'academic_class': academic_class,
                        'section': section,
                        'session': session,
                        'marked_by': request.user,
                        'institution': institution if institution else student.institution,
                    }
                )

                saved_count += 1

            except Student.DoesNotExist:
                errors.append(f"Student {student_id}: Not found")
                continue
            except Exception as e:
                errors.append(f"Student {student_id}: {str(e)}")
                continue

        if saved_count > 0:
            return JsonResponse({
                'success': True,
                'message': f'Successfully saved {saved_count} attendance records',
                'saved_count': saved_count,
                'errors': errors if errors else None
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No attendance records were saved',
                'errors': errors
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================
# ATTENDANCE REPORTS
# ============================================

@login_required
def attendance_report_form(request):
    """Form for generating attendance reports"""

    # Get user's institution
    institution = getattr(request.user, 'institution', None)

    if request.method == 'POST':
        # Process form and redirect to report
        report_type = request.POST.get('report_type')  # teacher or student
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        class_id = request.POST.get('academic_class')

        params = f"?type={report_type}&start={start_date}&end={end_date}"
        if class_id:
            params += f"&class={class_id}"

        return redirect(f"/attendance/report/{params}")

    # Get classes for dropdown
    if institution:
        classes = AcademicClass.objects.filter(institution=institution).order_by('name')
    else:
        classes = AcademicClass.objects.all().order_by('name')

    context = {
        'classes': classes,
    }

    return render(request, 'student_management/teachers/attendance_report_form.html', context)
