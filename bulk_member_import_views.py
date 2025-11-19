"""
Bulk Library Member Import Views
Add these functions to your student_management/views.py

Features:
- Download formatted Excel/CSV template for bulk member import
- Upload and validate member data
- Preview members before importing
- Detailed error reporting with row numbers
- Support for Excel (.xlsx) and CSV formats
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
import csv
import io

# For Excel support
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from .models import LibraryMember, Student


@login_required
def download_member_import_template(request):
    """
    Generate and download Excel or CSV template for bulk member import
    """
    file_format = request.GET.get('format', 'excel').lower()

    if file_format == 'excel' and EXCEL_AVAILABLE:
        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Library Member Import"

        # Instructions (rows 1-7)
        instructions = [
            "LIBRARY MEMBER BULK IMPORT TEMPLATE",
            "Instructions:",
            "1. Do not modify the column headers (row 8)",
            "2. Fill data starting from row 10 (row 9 is a sample - delete it before upload)",
            "3. Required fields: student_id, library_id",
            "4. Valid status values: active, suspended, expired",
            "5. Save and upload this file",
        ]

        for i, instruction in enumerate(instructions, 1):
            cell = ws.cell(row=i, column=1, value=instruction)
            cell.font = Font(bold=True, color='FF0000', size=11)

        # Headers (row 8)
        headers = [
            'student_id',          # Required - to lookup student
            'library_id',          # Required - unique library card number
            'joined_on',           # Optional - format: YYYY-MM-DD (default: today)
            'valid_until',         # Optional - format: YYYY-MM-DD (default: 1 year from joined_on)
            'status',              # Optional - active/suspended/expired (default: active)
            'max_books_allowed',   # Optional - integer (default: 3)
            'current_books_count', # Optional - integer (default: 0)
            'total_books_borrowed',# Optional - integer (default: 0)
            'total_fines_paid',    # Optional - decimal (default: 0.00)
            'outstanding_fine',    # Optional - decimal (default: 0.00)
            'notes',               # Optional - text
        ]

        header_row = 8
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF', size=11)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Sample data (row 9)
        sample_data = [
            'STU001',                           # student_id
            'LIB2024001',                       # library_id
            date.today().strftime('%Y-%m-%d'),  # joined_on
            (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),  # valid_until
            'active',                           # status
            '3',                                # max_books_allowed
            '0',                                # current_books_count
            '0',                                # total_books_borrowed
            '0.00',                             # total_fines_paid
            '0.00',                             # outstanding_fine
            'New member',                       # notes
        ]

        sample_row = 9
        for col, value in enumerate(sample_data, 1):
            cell = ws.cell(row=sample_row, column=col, value=value)
            cell.font = Font(italic=True, color='808080')

        # Adjust column widths
        column_widths = [15, 15, 12, 12, 12, 18, 20, 22, 18, 18, 30]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=library_member_import_template.xlsx'
        wb.save(response)
        return response

    else:
        # Create CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=library_member_import_template.csv'

        writer = csv.writer(response)

        # Instructions
        writer.writerow(['LIBRARY MEMBER BULK IMPORT TEMPLATE'])
        writer.writerow(['Instructions:'])
        writer.writerow(['1. Do not modify the column headers'])
        writer.writerow(['2. Fill data starting from the row after sample data'])
        writer.writerow(['3. Required fields: student_id, library_id'])
        writer.writerow(['4. Valid status values: active, suspended, expired'])
        writer.writerow(['5. Save and upload this file'])
        writer.writerow([])  # Empty row

        # Headers
        headers = [
            'student_id', 'library_id', 'joined_on', 'valid_until', 'status',
            'max_books_allowed', 'current_books_count', 'total_books_borrowed',
            'total_fines_paid', 'outstanding_fine', 'notes'
        ]
        writer.writerow(headers)

        # Sample data
        sample_data = [
            'STU001', 'LIB2024001', date.today().strftime('%Y-%m-%d'),
            (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'active', '3', '0', '0', '0.00', '0.00', 'New member'
        ]
        writer.writerow(sample_data)

        return response


@login_required
def bulk_member_import(request):
    """
    Handle bulk member import - upload, validate, preview, and import
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'preview')

        if action == 'preview':
            # Handle file upload and validation
            uploaded_file = request.FILES.get('member_file')

            if not uploaded_file:
                messages.error(request, 'Please select a file to upload')
                return redirect('bulk_member_import')

            # Validate file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['xlsx', 'xls', 'csv']:
                messages.error(request, 'Invalid file format. Please upload Excel (.xlsx) or CSV (.csv) file')
                return redirect('bulk_member_import')

            # Parse file based on format
            if file_extension in ['xlsx', 'xls']:
                members_data, errors = parse_member_excel_file(uploaded_file)
            else:
                members_data, errors = parse_member_csv_file(uploaded_file)

            if errors:
                # Show errors
                return render(request, 'student_management/library/bulk_import_member_errors.html', {
                    'errors': errors,
                    'total_errors': len(errors),
                    'success_count': len(members_data)
                })

            # Show preview
            return render(request, 'student_management/library/bulk_import_member_preview.html', {
                'members': members_data,
                'total_count': len(members_data)
            })

        elif action == 'import':
            # Import members from form data
            members_data = []
            i = 0
            while True:
                student_id = request.POST.get(f'student_id_{i}')
                if not student_id:
                    break

                member_data = {
                    'student_id': student_id,
                    'library_id': request.POST.get(f'library_id_{i}'),
                    'joined_on': request.POST.get(f'joined_on_{i}'),
                    'valid_until': request.POST.get(f'valid_until_{i}'),
                    'status': request.POST.get(f'status_{i}'),
                    'max_books_allowed': request.POST.get(f'max_books_allowed_{i}'),
                    'current_books_count': request.POST.get(f'current_books_count_{i}'),
                    'total_books_borrowed': request.POST.get(f'total_books_borrowed_{i}'),
                    'total_fines_paid': request.POST.get(f'total_fines_paid_{i}'),
                    'outstanding_fine': request.POST.get(f'outstanding_fine_{i}'),
                    'notes': request.POST.get(f'notes_{i}'),
                }
                members_data.append(member_data)
                i += 1

            # Import members
            imported_count = 0
            for member_data in members_data:
                try:
                    # Get student
                    student = Student.objects.get(id=member_data['student_id'])

                    # Create member
                    LibraryMember.objects.create(
                        student=student,
                        library_id=member_data['library_id'],
                        joined_on=member_data['joined_on'] or date.today(),
                        valid_until=member_data['valid_until'] or None,
                        status=member_data['status'] or 'active',
                        max_books_allowed=int(member_data['max_books_allowed'] or 3),
                        current_books_count=int(member_data['current_books_count'] or 0),
                        total_books_borrowed=int(member_data['total_books_borrowed'] or 0),
                        total_fines_paid=Decimal(member_data['total_fines_paid'] or '0.00'),
                        outstanding_fine=Decimal(member_data['outstanding_fine'] or '0.00'),
                        notes=member_data['notes'] or '',
                    )
                    imported_count += 1
                except Exception as e:
                    messages.error(request, f'Error importing member {member_data["library_id"]}: {str(e)}')

            messages.success(request, f'Successfully imported {imported_count} library members')
            return redirect('library_member_list')

    # GET request - show upload form
    return render(request, 'student_management/library/bulk_import_member_form.html', {
        'excel_available': EXCEL_AVAILABLE
    })


def parse_member_excel_file(uploaded_file):
    """
    Parse Excel file and extract member data
    Returns: (members_data, errors)
    """
    members_data = []
    errors = []

    try:
        wb = openpyxl.load_workbook(uploaded_file)
        ws = wb.active

        # Find header row (should be row 8 based on template)
        header_row = None
        for row_num in range(1, 15):
            cell_value = ws.cell(row=row_num, column=1).value
            if cell_value and str(cell_value).strip().lower() == 'student_id':
                header_row = row_num
                break

        if not header_row:
            errors.append('Could not find header row. Please use the template format.')
            return members_data, errors

        # Get headers
        headers = []
        for col in range(1, 12):  # 11 columns
            header = ws.cell(row=header_row, column=col).value
            headers.append(str(header).strip().lower() if header else '')

        # Process data rows
        for row_num in range(header_row + 1, ws.max_row + 1):
            # Skip sample row (usually row 9 in template)
            first_cell = ws.cell(row=row_num, column=1).value
            if not first_cell or str(first_cell).strip() == '':
                continue

            # Check if this is sample data row
            if str(first_cell).strip().upper() == 'STU001':
                continue

            row_data = {}
            row_errors = []

            # Extract data from each column
            for col_idx, header in enumerate(headers, 1):
                cell_value = ws.cell(row=row_num, column=col_idx).value
                row_data[header] = str(cell_value).strip() if cell_value else ''

            # Validate required fields
            if not row_data.get('student_id'):
                row_errors.append(f'Row {row_num}: Student ID is required')

            if not row_data.get('library_id'):
                row_errors.append(f'Row {row_num}: Library ID is required')

            # Validate student exists
            if row_data.get('student_id'):
                try:
                    student = Student.objects.get(id=row_data['student_id'])
                    row_data['student_obj'] = student
                    row_data['student_name'] = f"{student.first_name} {student.last_name}"

                    # Check if student already has library membership
                    if LibraryMember.objects.filter(student=student).exists():
                        row_errors.append(f'Row {row_num}: Student {row_data["student_id"]} already has a library membership')
                except Student.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Student with ID {row_data["student_id"]} not found')

            # Validate library_id uniqueness
            if row_data.get('library_id'):
                if LibraryMember.objects.filter(library_id=row_data['library_id']).exists():
                    row_errors.append(f'Row {row_num}: Library ID {row_data["library_id"]} already exists')

            # Validate status
            if row_data.get('status'):
                if row_data['status'].lower() not in ['active', 'suspended', 'expired', '']:
                    row_errors.append(f'Row {row_num}: Invalid status. Use: active, suspended, or expired')

            # Validate integer fields
            int_fields = ['max_books_allowed', 'current_books_count', 'total_books_borrowed']
            for field in int_fields:
                if row_data.get(field):
                    try:
                        row_data[field] = int(float(row_data[field]))
                    except (ValueError, InvalidOperation):
                        row_errors.append(f'Row {row_num}: {field} must be a valid integer')

            # Validate decimal fields
            decimal_fields = ['total_fines_paid', 'outstanding_fine']
            for field in decimal_fields:
                if row_data.get(field):
                    try:
                        row_data[field] = Decimal(row_data[field])
                    except (ValueError, InvalidOperation):
                        row_errors.append(f'Row {row_num}: {field} must be a valid decimal number')

            # Validate dates
            date_fields = ['joined_on', 'valid_until']
            for field in date_fields:
                if row_data.get(field) and row_data[field]:
                    try:
                        # Try to parse date
                        if isinstance(ws.cell(row=row_num, column=headers.index(field) + 1).value, date):
                            row_data[field] = ws.cell(row=row_num, column=headers.index(field) + 1).value
                        else:
                            # Parse string date
                            date_str = row_data[field]
                            if date_str:
                                from datetime import datetime
                                row_data[field] = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except (ValueError, AttributeError):
                        row_errors.append(f'Row {row_num}: {field} must be in YYYY-MM-DD format')

            if row_errors:
                errors.extend(row_errors)
            else:
                members_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading Excel file: {str(e)}')

    return members_data, errors


def parse_member_csv_file(uploaded_file):
    """
    Parse CSV file and extract member data
    Returns: (members_data, errors)
    """
    members_data = []
    errors = []

    try:
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(file_content))

        # Normalize header names
        fieldnames = [field.strip().lower() for field in csv_reader.fieldnames]

        # Check required headers
        if 'student_id' not in fieldnames or 'library_id' not in fieldnames:
            errors.append('Missing required columns. Please use the template format.')
            return members_data, errors

        row_num = 2  # Start from 2 (1 is header)

        for row in csv_reader:
            row_num += 1

            # Normalize row keys
            row_data = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}

            # Skip empty rows
            if not row_data.get('student_id'):
                continue

            # Skip sample data
            if row_data.get('student_id').upper() == 'STU001':
                continue

            row_errors = []

            # Validate required fields
            if not row_data.get('student_id'):
                row_errors.append(f'Row {row_num}: Student ID is required')

            if not row_data.get('library_id'):
                row_errors.append(f'Row {row_num}: Library ID is required')

            # Validate student exists
            if row_data.get('student_id'):
                try:
                    student = Student.objects.get(id=row_data['student_id'])
                    row_data['student_obj'] = student
                    row_data['student_name'] = f"{student.first_name} {student.last_name}"

                    # Check if student already has library membership
                    if LibraryMember.objects.filter(student=student).exists():
                        row_errors.append(f'Row {row_num}: Student {row_data["student_id"]} already has a library membership')
                except Student.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Student with ID {row_data["student_id"]} not found')

            # Validate library_id uniqueness
            if row_data.get('library_id'):
                if LibraryMember.objects.filter(library_id=row_data['library_id']).exists():
                    row_errors.append(f'Row {row_num}: Library ID {row_data["library_id"]} already exists')

            # Validate status
            if row_data.get('status'):
                if row_data['status'].lower() not in ['active', 'suspended', 'expired', '']:
                    row_errors.append(f'Row {row_num}: Invalid status. Use: active, suspended, or expired')

            # Validate integer fields
            int_fields = ['max_books_allowed', 'current_books_count', 'total_books_borrowed']
            for field in int_fields:
                if row_data.get(field):
                    try:
                        row_data[field] = int(float(row_data[field]))
                    except (ValueError, InvalidOperation):
                        row_errors.append(f'Row {row_num}: {field} must be a valid integer')

            # Validate decimal fields
            decimal_fields = ['total_fines_paid', 'outstanding_fine']
            for field in decimal_fields:
                if row_data.get(field):
                    try:
                        row_data[field] = Decimal(row_data[field])
                    except (ValueError, InvalidOperation):
                        row_errors.append(f'Row {row_num}: {field} must be a valid decimal number')

            # Validate dates
            date_fields = ['joined_on', 'valid_until']
            for field in date_fields:
                if row_data.get(field) and row_data[field]:
                    try:
                        from datetime import datetime
                        row_data[field] = datetime.strptime(row_data[field], '%Y-%m-%d').date()
                    except ValueError:
                        row_errors.append(f'Row {row_num}: {field} must be in YYYY-MM-DD format')

            if row_errors:
                errors.extend(row_errors)
            else:
                members_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading CSV file: {str(e)}')

    return members_data, errors
