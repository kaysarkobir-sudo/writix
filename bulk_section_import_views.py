"""
Bulk Class Section Import Views
Add these functions to your student_management/views.py

Features:
- Download formatted Excel/CSV template for bulk class section import
- Upload and validate section data
- Preview sections before importing
- Detailed error reporting with row numbers
- Support for Excel (.xlsx) and CSV formats
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
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

from .models import Section, AcademicClass, Teacher


@login_required
def download_section_import_template(request):
    """
    Generate and download Excel or CSV template for bulk section import
    """
    file_format = request.GET.get('format', 'excel').lower()

    if file_format == 'excel' and EXCEL_AVAILABLE:
        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Section Import"

        # Instructions (rows 1-8)
        instructions = [
            "CLASS SECTION BULK IMPORT TEMPLATE",
            "Instructions:",
            "1. Do not modify the column headers (row 9)",
            "2. Fill data starting from row 11 (row 10 is a sample - delete it before upload)",
            "3. Required fields: academic_class_id, name",
            "4. Optional fields: capacity, room_number, class_teacher_id, is_active",
            "5. is_active: Use 'true' or 'false' (default: true)",
            "6. Save and upload this file",
        ]

        for i, instruction in enumerate(instructions, 1):
            cell = ws.cell(row=i, column=1, value=instruction)
            cell.font = Font(bold=True, color='FF0000', size=11)

        # Headers (row 9)
        headers = [
            'academic_class_id',  # Required - Academic Class ID from database
            'name',              # Required - Section name (e.g., "A", "B", "Morning")
            'capacity',          # Optional - Maximum number of students
            'room_number',       # Optional - Room number/name
            'class_teacher_id',  # Optional - Class Teacher ID from database
            'is_active',         # Optional - true/false (default: true)
        ]

        header_row = 9
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF', size=11)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Sample data (row 10)
        sample_data = [
            '1',        # academic_class_id
            'A',        # name
            '40',       # capacity
            'Room 101', # room_number
            '1',        # class_teacher_id
            'true',     # is_active
        ]

        sample_row = 10
        for col, value in enumerate(sample_data, 1):
            cell = ws.cell(row=sample_row, column=col, value=value)
            cell.font = Font(italic=True, color='808080')

        # Adjust column widths
        column_widths = [20, 20, 12, 15, 20, 12]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=section_import_template.xlsx'
        wb.save(response)
        return response

    else:
        # Create CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=section_import_template.csv'

        writer = csv.writer(response)

        # Instructions
        writer.writerow(['CLASS SECTION BULK IMPORT TEMPLATE'])
        writer.writerow(['Instructions:'])
        writer.writerow(['1. Do not modify the column headers'])
        writer.writerow(['2. Fill data starting from the row after sample data'])
        writer.writerow(['3. Required fields: academic_class_id, name'])
        writer.writerow(['4. Optional fields: capacity, room_number, class_teacher_id, is_active'])
        writer.writerow(['5. is_active: Use true or false (default: true)'])
        writer.writerow(['6. Save and upload this file'])
        writer.writerow([])  # Empty row

        # Headers
        headers = ['academic_class_id', 'name', 'capacity', 'room_number', 'class_teacher_id', 'is_active']
        writer.writerow(headers)

        # Sample data
        sample_data = ['1', 'A', '40', 'Room 101', '1', 'true']
        writer.writerow(sample_data)

        return response


@login_required
def bulk_section_import(request):
    """
    Handle bulk section import - upload, validate, preview, and import
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'preview')

        if action == 'preview':
            # Handle file upload and validation
            uploaded_file = request.FILES.get('section_file')

            if not uploaded_file:
                messages.error(request, 'Please select a file to upload')
                return redirect('bulk_section_import')

            # Validate file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['xlsx', 'xls', 'csv']:
                messages.error(request, 'Invalid file format. Please upload Excel (.xlsx) or CSV (.csv) file')
                return redirect('bulk_section_import')

            # Parse file based on format
            if file_extension in ['xlsx', 'xls']:
                sections_data, errors = parse_section_excel_file(uploaded_file, request.user.institution)
            else:
                sections_data, errors = parse_section_csv_file(uploaded_file, request.user.institution)

            if errors:
                # Show errors
                return render(request, 'student_management/academic/bulk_import_section_errors.html', {
                    'errors': errors,
                    'total_errors': len(errors),
                    'success_count': len(sections_data)
                })

            # Show preview
            return render(request, 'student_management/academic/bulk_import_section_preview.html', {
                'sections': sections_data,
                'total_count': len(sections_data)
            })

        elif action == 'import':
            # Import sections from form data
            sections_data = []
            i = 0
            while True:
                academic_class_id = request.POST.get(f'academic_class_id_{i}')
                if not academic_class_id:
                    break

                section_data = {
                    'academic_class_id': academic_class_id,
                    'name': request.POST.get(f'name_{i}'),
                    'capacity': request.POST.get(f'capacity_{i}'),
                    'room_number': request.POST.get(f'room_number_{i}'),
                    'class_teacher_id': request.POST.get(f'class_teacher_id_{i}'),
                    'is_active': request.POST.get(f'is_active_{i}', 'true'),
                }
                sections_data.append(section_data)
                i += 1

            # Import sections
            imported_count = 0
            for section_data in sections_data:
                try:
                    # Get institution from request user
                    institution = request.user.institution

                    # Get academic class
                    academic_class = AcademicClass.objects.get(id=section_data['academic_class_id'])

                    # Get teacher if provided
                    class_teacher = None
                    if section_data['class_teacher_id']:
                        try:
                            class_teacher = Teacher.objects.get(id=section_data['class_teacher_id'])
                        except Teacher.DoesNotExist:
                            pass

                    # Parse capacity
                    capacity = None
                    if section_data['capacity']:
                        try:
                            capacity = int(section_data['capacity'])
                        except ValueError:
                            pass

                    # Parse is_active
                    is_active = section_data['is_active'].lower() in ['true', 'yes', '1', 't', 'y']

                    # Create section
                    Section.objects.create(
                        institution=institution,
                        academic_class=academic_class,
                        name=section_data['name'],
                        capacity=capacity,
                        room_number=section_data['room_number'] or '',
                        class_teacher=class_teacher,
                        is_active=is_active,
                    )
                    imported_count += 1
                except Exception as e:
                    messages.error(request, f'Error importing section {section_data["name"]}: {str(e)}')

            messages.success(request, f'Successfully imported {imported_count} class sections')
            return redirect('class_section_list')

    # GET request - show upload form
    return render(request, 'student_management/academic/bulk_import_section_form.html', {
        'excel_available': EXCEL_AVAILABLE
    })


def parse_section_excel_file(uploaded_file, institution):
    """
    Parse Excel file and extract section data
    Returns: (sections_data, errors)
    """
    sections_data = []
    errors = []

    try:
        wb = openpyxl.load_workbook(uploaded_file)
        ws = wb.active

        # Find header row (should be row 9 based on template)
        header_row = None
        for row_num in range(1, 20):
            cell_value = ws.cell(row=row_num, column=1).value
            if cell_value and str(cell_value).strip().lower() == 'academic_class_id':
                header_row = row_num
                break

        if not header_row:
            errors.append('Could not find header row. Please use the template format.')
            return sections_data, errors

        # Get headers
        headers = []
        for col in range(1, 7):  # 6 columns
            header = ws.cell(row=header_row, column=col).value
            headers.append(str(header).strip().lower() if header else '')

        # Process data rows
        for row_num in range(header_row + 1, ws.max_row + 1):
            # Skip empty rows
            first_cell = ws.cell(row=row_num, column=1).value
            if not first_cell or str(first_cell).strip() == '':
                continue

            # Check if this is sample data row (academic_class_id = 1 and name = A)
            if str(first_cell).strip() == '1':
                second_cell = ws.cell(row=row_num, column=2).value
                if str(second_cell).strip().upper() == 'A':
                    # This might be sample data, skip it
                    continue

            row_data = {}
            row_errors = []

            # Extract data from each column
            for col_idx, header in enumerate(headers, 1):
                cell_value = ws.cell(row=row_num, column=col_idx).value
                row_data[header] = str(cell_value).strip() if cell_value else ''

            # Validate required fields
            if not row_data.get('academic_class_id'):
                row_errors.append(f'Row {row_num}: Academic Class ID is required')

            if not row_data.get('name'):
                row_errors.append(f'Row {row_num}: Section name is required')

            # Validate academic class exists
            if row_data.get('academic_class_id'):
                try:
                    academic_class = AcademicClass.objects.get(id=row_data['academic_class_id'])

                    # Check if section with same name already exists for this class
                    if Section.objects.filter(
                        academic_class=academic_class,
                        name=row_data.get('name', '')
                    ).exists():
                        row_errors.append(f'Row {row_num}: Section "{row_data.get("name")}" already exists for this class')

                    # Store class info for preview
                    row_data['class_name'] = str(academic_class)
                except AcademicClass.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Academic Class with ID {row_data["academic_class_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid academic class ID format')

            # Validate capacity (if provided)
            if row_data.get('capacity'):
                try:
                    capacity = int(row_data['capacity'])
                    if capacity < 1:
                        row_errors.append(f'Row {row_num}: Capacity must be a positive number')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Capacity must be a valid number')

            # Validate teacher exists (if provided)
            if row_data.get('class_teacher_id'):
                try:
                    teacher = Teacher.objects.get(id=row_data['class_teacher_id'])
                    # Store teacher info for preview
                    row_data['teacher_name'] = str(teacher)
                except Teacher.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Teacher with ID {row_data["class_teacher_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid teacher ID format')

            # Validate is_active (if provided)
            if row_data.get('is_active'):
                if row_data['is_active'].lower() not in ['true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n', '']:
                    row_errors.append(f'Row {row_num}: is_active must be "true" or "false"')

            if row_errors:
                errors.extend(row_errors)
            else:
                sections_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading Excel file: {str(e)}')

    return sections_data, errors


def parse_section_csv_file(uploaded_file, institution):
    """
    Parse CSV file and extract section data
    Returns: (sections_data, errors)
    """
    sections_data = []
    errors = []

    try:
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(file_content))

        # Normalize header names
        fieldnames = [field.strip().lower() for field in csv_reader.fieldnames]

        # Check required headers
        if 'academic_class_id' not in fieldnames or 'name' not in fieldnames:
            errors.append('Missing required columns. Please use the template format.')
            return sections_data, errors

        row_num = 2  # Start from 2 (1 is header)

        for row in csv_reader:
            row_num += 1

            # Normalize row keys
            row_data = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}

            # Skip empty rows
            if not row_data.get('academic_class_id'):
                continue

            # Skip sample data (academic_class_id = 1 and name = A)
            if row_data.get('academic_class_id') == '1' and row_data.get('name', '').upper() == 'A':
                continue

            row_errors = []

            # Validate required fields
            if not row_data.get('academic_class_id'):
                row_errors.append(f'Row {row_num}: Academic Class ID is required')

            if not row_data.get('name'):
                row_errors.append(f'Row {row_num}: Section name is required')

            # Validate academic class exists
            if row_data.get('academic_class_id'):
                try:
                    academic_class = AcademicClass.objects.get(id=row_data['academic_class_id'])

                    # Check if section with same name already exists for this class
                    if Section.objects.filter(
                        academic_class=academic_class,
                        name=row_data.get('name', '')
                    ).exists():
                        row_errors.append(f'Row {row_num}: Section "{row_data.get("name")}" already exists for this class')

                    # Store class info for preview
                    row_data['class_name'] = str(academic_class)
                except AcademicClass.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Academic Class with ID {row_data["academic_class_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid academic class ID format')

            # Validate capacity (if provided)
            if row_data.get('capacity'):
                try:
                    capacity = int(row_data['capacity'])
                    if capacity < 1:
                        row_errors.append(f'Row {row_num}: Capacity must be a positive number')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Capacity must be a valid number')

            # Validate teacher exists (if provided)
            if row_data.get('class_teacher_id'):
                try:
                    teacher = Teacher.objects.get(id=row_data['class_teacher_id'])
                    # Store teacher info for preview
                    row_data['teacher_name'] = str(teacher)
                except Teacher.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Teacher with ID {row_data["class_teacher_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid teacher ID format')

            # Validate is_active (if provided)
            if row_data.get('is_active'):
                if row_data['is_active'].lower() not in ['true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n', '']:
                    row_errors.append(f'Row {row_num}: is_active must be "true" or "false"')

            if row_errors:
                errors.extend(row_errors)
            else:
                sections_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading CSV file: {str(e)}')

    return sections_data, errors
