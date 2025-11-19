"""
Bulk Transport Member Import Views
Add these functions to your student_management/views.py

Features:
- Download formatted Excel/CSV template for bulk transport member import
- Upload and validate transport member data
- Preview members before importing
- Detailed error reporting with row numbers
- Support for Excel (.xlsx) and CSV formats
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import date
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

from .models import TransportMember, Student, TransportRoute, Vehicle


@login_required
def download_transport_member_import_template(request):
    """
    Generate and download Excel or CSV template for bulk transport member import
    """
    file_format = request.GET.get('format', 'excel').lower()

    if file_format == 'excel' and EXCEL_AVAILABLE:
        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transport Member Import"

        # Instructions (rows 1-8)
        instructions = [
            "TRANSPORT MEMBER BULK IMPORT TEMPLATE",
            "Instructions:",
            "1. Do not modify the column headers (row 9)",
            "2. Fill data starting from row 11 (row 10 is a sample - delete it before upload)",
            "3. Required fields: student_id, route_id",
            "4. Optional fields: vehicle_id, pickup, dropoff, joined_at, note",
            "5. Date format: YYYY-MM-DD (e.g., 2024-01-15)",
            "6. Save and upload this file",
        ]

        for i, instruction in enumerate(instructions, 1):
            cell = ws.cell(row=i, column=1, value=instruction)
            cell.font = Font(bold=True, color='FF0000', size=11)

        # Headers (row 9)
        headers = [
            'student_id',    # Required - Student ID from database
            'route_id',      # Required - Route ID from database
            'vehicle_id',    # Optional - Vehicle ID from database
            'pickup',        # Optional - Pickup point location
            'dropoff',       # Optional - Drop-off point location
            'joined_at',     # Optional - Date joined (YYYY-MM-DD)
            'note',          # Optional - Additional notes
        ]

        header_row = 9
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF', size=11)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Sample data (row 10)
        sample_data = [
            '1',                      # student_id
            '1',                      # route_id
            '1',                      # vehicle_id
            'Mirpur 10 Circle',       # pickup
            'School Main Gate',       # dropoff
            '2024-01-15',             # joined_at
            'Morning route',          # note
        ]

        sample_row = 10
        for col, value in enumerate(sample_data, 1):
            cell = ws.cell(row=sample_row, column=col, value=value)
            cell.font = Font(italic=True, color='808080')

        # Adjust column widths
        column_widths = [15, 15, 15, 25, 25, 15, 30]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=transport_member_import_template.xlsx'
        wb.save(response)
        return response

    else:
        # Create CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=transport_member_import_template.csv'

        writer = csv.writer(response)

        # Instructions
        writer.writerow(['TRANSPORT MEMBER BULK IMPORT TEMPLATE'])
        writer.writerow(['Instructions:'])
        writer.writerow(['1. Do not modify the column headers'])
        writer.writerow(['2. Fill data starting from the row after sample data'])
        writer.writerow(['3. Required fields: student_id, route_id'])
        writer.writerow(['4. Optional fields: vehicle_id, pickup, dropoff, joined_at, note'])
        writer.writerow(['5. Date format: YYYY-MM-DD (e.g., 2024-01-15)'])
        writer.writerow(['6. Save and upload this file'])
        writer.writerow([])  # Empty row

        # Headers
        headers = ['student_id', 'route_id', 'vehicle_id', 'pickup', 'dropoff', 'joined_at', 'note']
        writer.writerow(headers)

        # Sample data
        sample_data = ['1', '1', '1', 'Mirpur 10 Circle', 'School Main Gate', '2024-01-15', 'Morning route']
        writer.writerow(sample_data)

        return response


@login_required
def bulk_transport_member_import(request):
    """
    Handle bulk transport member import - upload, validate, preview, and import
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'preview')

        if action == 'preview':
            # Handle file upload and validation
            uploaded_file = request.FILES.get('member_file')

            if not uploaded_file:
                messages.error(request, 'Please select a file to upload')
                return redirect('bulk_transport_member_import')

            # Validate file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['xlsx', 'xls', 'csv']:
                messages.error(request, 'Invalid file format. Please upload Excel (.xlsx) or CSV (.csv) file')
                return redirect('bulk_transport_member_import')

            # Parse file based on format
            if file_extension in ['xlsx', 'xls']:
                members_data, errors = parse_transport_member_excel_file(uploaded_file, request.user.institution)
            else:
                members_data, errors = parse_transport_member_csv_file(uploaded_file, request.user.institution)

            if errors:
                # Show errors
                return render(request, 'student_management/transport/bulk_import_member_errors.html', {
                    'errors': errors,
                    'total_errors': len(errors),
                    'success_count': len(members_data)
                })

            # Show preview
            return render(request, 'student_management/transport/bulk_import_member_preview.html', {
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
                    'route_id': request.POST.get(f'route_id_{i}'),
                    'vehicle_id': request.POST.get(f'vehicle_id_{i}'),
                    'pickup': request.POST.get(f'pickup_{i}'),
                    'dropoff': request.POST.get(f'dropoff_{i}'),
                    'joined_at': request.POST.get(f'joined_at_{i}'),
                    'note': request.POST.get(f'note_{i}'),
                }
                members_data.append(member_data)
                i += 1

            # Import members
            imported_count = 0
            for member_data in members_data:
                try:
                    # Get school from request user
                    school = request.user.institution

                    # Get student and route
                    student = Student.objects.get(id=member_data['student_id'])
                    route = TransportRoute.objects.get(id=member_data['route_id'])

                    # Get vehicle if provided
                    vehicle = None
                    if member_data['vehicle_id']:
                        try:
                            vehicle = Vehicle.objects.get(id=member_data['vehicle_id'])
                        except Vehicle.DoesNotExist:
                            pass

                    # Parse joined_at date
                    joined_at = date.today()
                    if member_data['joined_at']:
                        try:
                            joined_at = date.fromisoformat(member_data['joined_at'])
                        except ValueError:
                            pass

                    # Create transport member
                    TransportMember.objects.create(
                        school=school,
                        student=student,
                        route=route,
                        vehicle=vehicle,
                        pickup=member_data['pickup'] or '',
                        dropoff=member_data['dropoff'] or '',
                        joined_at=joined_at,
                        note=member_data['note'] or '',
                    )
                    imported_count += 1
                except Exception as e:
                    messages.error(request, f'Error importing member for student ID {member_data["student_id"]}: {str(e)}')

            messages.success(request, f'Successfully imported {imported_count} transport members')
            return redirect('member_list')

    # GET request - show upload form
    return render(request, 'student_management/transport/bulk_import_member_form.html', {
        'excel_available': EXCEL_AVAILABLE
    })


def parse_transport_member_excel_file(uploaded_file, school):
    """
    Parse Excel file and extract transport member data
    Returns: (members_data, errors)
    """
    members_data = []
    errors = []

    try:
        wb = openpyxl.load_workbook(uploaded_file)
        ws = wb.active

        # Find header row (should be row 9 based on template)
        header_row = None
        for row_num in range(1, 20):
            cell_value = ws.cell(row=row_num, column=1).value
            if cell_value and str(cell_value).strip().lower() == 'student_id':
                header_row = row_num
                break

        if not header_row:
            errors.append('Could not find header row. Please use the template format.')
            return members_data, errors

        # Get headers
        headers = []
        for col in range(1, 8):  # 7 columns
            header = ws.cell(row=header_row, column=col).value
            headers.append(str(header).strip().lower() if header else '')

        # Process data rows
        for row_num in range(header_row + 1, ws.max_row + 1):
            # Skip sample row
            first_cell = ws.cell(row=row_num, column=1).value
            if not first_cell or str(first_cell).strip() == '':
                continue

            # Check if this is sample data row (student_id = 1 and route_id = 1)
            if str(first_cell).strip() == '1':
                second_cell = ws.cell(row=row_num, column=2).value
                if str(second_cell).strip() == '1':
                    # This might be sample data, skip it
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

            if not row_data.get('route_id'):
                row_errors.append(f'Row {row_num}: Route ID is required')

            # Validate student exists
            if row_data.get('student_id'):
                try:
                    student = Student.objects.get(id=row_data['student_id'])

                    # Check if student already has transport membership
                    if TransportMember.objects.filter(student=student).exists():
                        row_errors.append(f'Row {row_num}: Student ID {row_data["student_id"]} already has transport membership')

                    # Store student info for preview
                    row_data['student_name'] = str(student)
                except Student.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Student with ID {row_data["student_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid student ID format')

            # Validate route exists
            if row_data.get('route_id'):
                try:
                    route = TransportRoute.objects.get(id=row_data['route_id'])
                    # Store route info for preview
                    row_data['route_name'] = route.name
                except TransportRoute.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Route with ID {row_data["route_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid route ID format')

            # Validate vehicle exists (if provided)
            if row_data.get('vehicle_id'):
                try:
                    vehicle = Vehicle.objects.get(id=row_data['vehicle_id'])
                    # Store vehicle info for preview
                    row_data['vehicle_number'] = vehicle.vehicle_number
                except Vehicle.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Vehicle with ID {row_data["vehicle_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid vehicle ID format')

            # Validate joined_at date (if provided)
            if row_data.get('joined_at'):
                try:
                    # Try to parse date in YYYY-MM-DD format
                    date.fromisoformat(str(row_data['joined_at']))
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid date format for joined_at. Use YYYY-MM-DD (e.g., 2024-01-15)')

            if row_errors:
                errors.extend(row_errors)
            else:
                members_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading Excel file: {str(e)}')

    return members_data, errors


def parse_transport_member_csv_file(uploaded_file, school):
    """
    Parse CSV file and extract transport member data
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
        if 'student_id' not in fieldnames or 'route_id' not in fieldnames:
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

            # Skip sample data (student_id = 1 and route_id = 1)
            if row_data.get('student_id') == '1' and row_data.get('route_id') == '1':
                continue

            row_errors = []

            # Validate required fields
            if not row_data.get('student_id'):
                row_errors.append(f'Row {row_num}: Student ID is required')

            if not row_data.get('route_id'):
                row_errors.append(f'Row {row_num}: Route ID is required')

            # Validate student exists
            if row_data.get('student_id'):
                try:
                    student = Student.objects.get(id=row_data['student_id'])

                    # Check if student already has transport membership
                    if TransportMember.objects.filter(student=student).exists():
                        row_errors.append(f'Row {row_num}: Student ID {row_data["student_id"]} already has transport membership')

                    # Store student info for preview
                    row_data['student_name'] = str(student)
                except Student.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Student with ID {row_data["student_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid student ID format')

            # Validate route exists
            if row_data.get('route_id'):
                try:
                    route = TransportRoute.objects.get(id=row_data['route_id'])
                    # Store route info for preview
                    row_data['route_name'] = route.name
                except TransportRoute.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Route with ID {row_data["route_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid route ID format')

            # Validate vehicle exists (if provided)
            if row_data.get('vehicle_id'):
                try:
                    vehicle = Vehicle.objects.get(id=row_data['vehicle_id'])
                    # Store vehicle info for preview
                    row_data['vehicle_number'] = vehicle.vehicle_number
                except Vehicle.DoesNotExist:
                    row_errors.append(f'Row {row_num}: Vehicle with ID {row_data["vehicle_id"]} not found')
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid vehicle ID format')

            # Validate joined_at date (if provided)
            if row_data.get('joined_at'):
                try:
                    # Try to parse date in YYYY-MM-DD format
                    date.fromisoformat(str(row_data['joined_at']))
                except ValueError:
                    row_errors.append(f'Row {row_num}: Invalid date format for joined_at. Use YYYY-MM-DD (e.g., 2024-01-15)')

            if row_errors:
                errors.extend(row_errors)
            else:
                members_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading CSV file: {str(e)}')

    return members_data, errors
