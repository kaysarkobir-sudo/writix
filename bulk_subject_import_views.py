"""
Bulk Subject Import Views
Add these functions to your student_management/views.py

Features:
- Download formatted Excel/CSV template for bulk subject import
- Upload and validate subject data
- Preview subjects before importing
- Detailed error reporting with row numbers
- Support for Excel (.xlsx) and CSV formats
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import csv
import io

# For Excel support
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from .models import Subject


@login_required
def download_subject_import_template(request):
    """
    Generate and download Excel or CSV template for bulk subject import
    """
    file_format = request.GET.get('format', 'excel').lower()

    if file_format == 'excel' and EXCEL_AVAILABLE:
        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Subject Import"

        # Instructions (rows 1-8)
        instructions = [
            "SUBJECT BULK IMPORT TEMPLATE",
            "Instructions:",
            "1. Do not modify the column headers (row 9)",
            "2. Fill data starting from row 11 (row 10 is a sample - delete it before upload)",
            "3. Required field: name",
            "4. Optional fields: code, description, subject_type, is_active",
            "5. subject_type: Theory, Practical, Lab, or Both (default: Theory)",
            "6. is_active: Use 'true' or 'false' (default: true)",
            "7. Save and upload this file",
        ]

        for i, instruction in enumerate(instructions, 1):
            cell = ws.cell(row=i, column=1, value=instruction)
            cell.font = Font(bold=True, color='FF0000', size=11)

        # Headers (row 9)
        headers = [
            'name',          # Required - Subject name (e.g., "Mathematics", "English")
            'code',          # Optional - Subject code (e.g., "MATH101", "ENG201")
            'description',   # Optional - Subject description
            'subject_type',  # Optional - Theory, Practical, Lab, or Both
            'is_active',     # Optional - true/false (default: true)
        ]

        header_row = 9
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF', size=11)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Sample data (row 10)
        sample_data = [
            'Mathematics',                    # name
            'MATH101',                        # code
            'Basic Mathematics for Grade 10', # description
            'Theory',                         # subject_type
            'true',                           # is_active
        ]

        sample_row = 10
        for col, value in enumerate(sample_data, 1):
            cell = ws.cell(row=sample_row, column=col, value=value)
            cell.font = Font(italic=True, color='808080')

        # Adjust column widths
        column_widths = [25, 15, 40, 15, 12]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=subject_import_template.xlsx'
        wb.save(response)
        return response

    else:
        # Create CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=subject_import_template.csv'

        writer = csv.writer(response)

        # Instructions
        writer.writerow(['SUBJECT BULK IMPORT TEMPLATE'])
        writer.writerow(['Instructions:'])
        writer.writerow(['1. Do not modify the column headers'])
        writer.writerow(['2. Fill data starting from the row after sample data'])
        writer.writerow(['3. Required field: name'])
        writer.writerow(['4. Optional fields: code, description, subject_type, is_active'])
        writer.writerow(['5. subject_type: Theory, Practical, Lab, or Both (default: Theory)'])
        writer.writerow(['6. is_active: Use true or false (default: true)'])
        writer.writerow(['7. Save and upload this file'])
        writer.writerow([])  # Empty row

        # Headers
        headers = ['name', 'code', 'description', 'subject_type', 'is_active']
        writer.writerow(headers)

        # Sample data
        sample_data = ['Mathematics', 'MATH101', 'Basic Mathematics for Grade 10', 'Theory', 'true']
        writer.writerow(sample_data)

        return response


@login_required
def bulk_subject_import(request):
    """
    Handle bulk subject import - upload, validate, preview, and import
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'preview')

        if action == 'preview':
            # Handle file upload and validation
            uploaded_file = request.FILES.get('subject_file')

            if not uploaded_file:
                messages.error(request, 'Please select a file to upload')
                return redirect('bulk_subject_import')

            # Validate file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['xlsx', 'xls', 'csv']:
                messages.error(request, 'Invalid file format. Please upload Excel (.xlsx) or CSV (.csv) file')
                return redirect('bulk_subject_import')

            # Parse file based on format
            if file_extension in ['xlsx', 'xls']:
                subjects_data, errors = parse_subject_excel_file(uploaded_file, request.user.institution)
            else:
                subjects_data, errors = parse_subject_csv_file(uploaded_file, request.user.institution)

            if errors:
                # Show errors
                return render(request, 'student_management/academic/bulk_import_subject_errors.html', {
                    'errors': errors,
                    'total_errors': len(errors),
                    'success_count': len(subjects_data)
                })

            # Show preview
            return render(request, 'student_management/academic/bulk_import_subject_preview.html', {
                'subjects': subjects_data,
                'total_count': len(subjects_data)
            })

        elif action == 'import':
            # Import subjects from form data
            subjects_data = []
            i = 0
            while True:
                name = request.POST.get(f'name_{i}')
                if not name:
                    break

                subject_data = {
                    'name': name,
                    'code': request.POST.get(f'code_{i}'),
                    'description': request.POST.get(f'description_{i}'),
                    'subject_type': request.POST.get(f'subject_type_{i}'),
                    'is_active': request.POST.get(f'is_active_{i}', 'true'),
                }
                subjects_data.append(subject_data)
                i += 1

            # Import subjects
            imported_count = 0
            for subject_data in subjects_data:
                try:
                    # Get institution from request user
                    institution = request.user.institution

                    # Parse is_active
                    is_active = subject_data['is_active'].lower() in ['true', 'yes', '1', 't', 'y']

                    # Default subject_type if not provided
                    subject_type = subject_data['subject_type'] or 'Theory'

                    # Create subject
                    Subject.objects.create(
                        institution=institution,
                        name=subject_data['name'],
                        code=subject_data['code'] or '',
                        description=subject_data['description'] or '',
                        subject_type=subject_type,
                        is_active=is_active,
                    )
                    imported_count += 1
                except Exception as e:
                    messages.error(request, f'Error importing subject {subject_data["name"]}: {str(e)}')

            messages.success(request, f'Successfully imported {imported_count} subjects')
            return redirect('subject_list')

    # GET request - show upload form
    return render(request, 'student_management/academic/bulk_import_subject_form.html', {
        'excel_available': EXCEL_AVAILABLE
    })


def parse_subject_excel_file(uploaded_file, institution):
    """
    Parse Excel file and extract subject data
    Returns: (subjects_data, errors)
    """
    subjects_data = []
    errors = []

    try:
        wb = openpyxl.load_workbook(uploaded_file)
        ws = wb.active

        # Find header row (should be row 9 based on template)
        header_row = None
        for row_num in range(1, 20):
            cell_value = ws.cell(row=row_num, column=1).value
            if cell_value and str(cell_value).strip().lower() == 'name':
                header_row = row_num
                break

        if not header_row:
            errors.append('Could not find header row. Please use the template format.')
            return subjects_data, errors

        # Get headers
        headers = []
        for col in range(1, 6):  # 5 columns
            header = ws.cell(row=header_row, column=col).value
            headers.append(str(header).strip().lower() if header else '')

        # Process data rows
        for row_num in range(header_row + 1, ws.max_row + 1):
            # Skip empty rows
            first_cell = ws.cell(row=row_num, column=1).value
            if not first_cell or str(first_cell).strip() == '':
                continue

            # Check if this is sample data row (name = Mathematics and code = MATH101)
            if str(first_cell).strip() == 'Mathematics':
                second_cell = ws.cell(row=row_num, column=2).value
                if str(second_cell).strip() == 'MATH101':
                    # This might be sample data, skip it
                    continue

            row_data = {}
            row_errors = []

            # Extract data from each column
            for col_idx, header in enumerate(headers, 1):
                cell_value = ws.cell(row=row_num, column=col_idx).value
                row_data[header] = str(cell_value).strip() if cell_value else ''

            # Validate required fields
            if not row_data.get('name'):
                row_errors.append(f'Row {row_num}: Subject name is required')

            # Check if subject with same name already exists
            if row_data.get('name'):
                if Subject.objects.filter(
                    institution=institution,
                    name=row_data['name']
                ).exists():
                    row_errors.append(f'Row {row_num}: Subject "{row_data["name"]}" already exists')

            # Check if subject code already exists (if provided)
            if row_data.get('code'):
                if Subject.objects.filter(
                    institution=institution,
                    code=row_data['code']
                ).exists():
                    row_errors.append(f'Row {row_num}: Subject code "{row_data["code"]}" already exists')

            # Validate subject_type (if provided)
            if row_data.get('subject_type'):
                valid_types = ['theory', 'practical', 'lab', 'both', '']
                if row_data['subject_type'].lower() not in valid_types:
                    row_errors.append(f'Row {row_num}: subject_type must be: Theory, Practical, Lab, or Both')

            # Validate is_active (if provided)
            if row_data.get('is_active'):
                if row_data['is_active'].lower() not in ['true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n', '']:
                    row_errors.append(f'Row {row_num}: is_active must be "true" or "false"')

            if row_errors:
                errors.extend(row_errors)
            else:
                subjects_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading Excel file: {str(e)}')

    return subjects_data, errors


def parse_subject_csv_file(uploaded_file, institution):
    """
    Parse CSV file and extract subject data
    Returns: (subjects_data, errors)
    """
    subjects_data = []
    errors = []

    try:
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(file_content))

        # Normalize header names
        fieldnames = [field.strip().lower() for field in csv_reader.fieldnames]

        # Check required headers
        if 'name' not in fieldnames:
            errors.append('Missing required column: name. Please use the template format.')
            return subjects_data, errors

        row_num = 2  # Start from 2 (1 is header)

        for row in csv_reader:
            row_num += 1

            # Normalize row keys
            row_data = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}

            # Skip empty rows
            if not row_data.get('name'):
                continue

            # Skip sample data (name = Mathematics and code = MATH101)
            if row_data.get('name') == 'Mathematics' and row_data.get('code') == 'MATH101':
                continue

            row_errors = []

            # Validate required fields
            if not row_data.get('name'):
                row_errors.append(f'Row {row_num}: Subject name is required')

            # Check if subject with same name already exists
            if row_data.get('name'):
                if Subject.objects.filter(
                    institution=institution,
                    name=row_data['name']
                ).exists():
                    row_errors.append(f'Row {row_num}: Subject "{row_data["name"]}" already exists')

            # Check if subject code already exists (if provided)
            if row_data.get('code'):
                if Subject.objects.filter(
                    institution=institution,
                    code=row_data['code']
                ).exists():
                    row_errors.append(f'Row {row_num}: Subject code "{row_data["code"]}" already exists')

            # Validate subject_type (if provided)
            if row_data.get('subject_type'):
                valid_types = ['theory', 'practical', 'lab', 'both', '']
                if row_data['subject_type'].lower() not in valid_types:
                    row_errors.append(f'Row {row_num}: subject_type must be: Theory, Practical, Lab, or Both')

            # Validate is_active (if provided)
            if row_data.get('is_active'):
                if row_data['is_active'].lower() not in ['true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n', '']:
                    row_errors.append(f'Row {row_num}: is_active must be "true" or "false"')

            if row_errors:
                errors.extend(row_errors)
            else:
                subjects_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading CSV file: {str(e)}')

    return subjects_data, errors
