"""
Bulk Route Import Views
Add these functions to your student_management/views.py

Features:
- Download formatted Excel/CSV template for bulk route import
- Upload and validate route data
- Preview routes before importing
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

from .models import TransportRoute


@login_required
def download_route_import_template(request):
    """
    Generate and download Excel or CSV template for bulk route import
    """
    file_format = request.GET.get('format', 'excel').lower()

    if file_format == 'excel' and EXCEL_AVAILABLE:
        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Route Import"

        # Instructions (rows 1-7)
        instructions = [
            "ROUTE BULK IMPORT TEMPLATE",
            "Instructions:",
            "1. Do not modify the column headers (row 8)",
            "2. Fill data starting from row 10 (row 9 is a sample - delete it before upload)",
            "3. Required fields: name, start_point, end_point, fare",
            "4. Fare should be a number (e.g., 500, 750.50)",
            "5. Save and upload this file",
        ]

        for i, instruction in enumerate(instructions, 1):
            cell = ws.cell(row=i, column=1, value=instruction)
            cell.font = Font(bold=True, color='FF0000', size=11)

        # Headers (row 8)
        headers = [
            'name',          # Required - route name (e.g., Route 1, Mirpur Route)
            'start_point',   # Required - starting location
            'end_point',     # Required - ending location
            'fare',          # Required - fare amount (decimal)
            'note',          # Optional - additional notes
        ]

        header_row = 8
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF', size=11)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Sample data (row 9)
        sample_data = [
            'Route 1 - Mirpur',              # name
            'Mirpur 10',                     # start_point
            'School Campus',                 # end_point
            '500',                           # fare
            'Morning pickup at 7:00 AM',     # note
        ]

        sample_row = 9
        for col, value in enumerate(sample_data, 1):
            cell = ws.cell(row=sample_row, column=col, value=value)
            cell.font = Font(italic=True, color='808080')

        # Adjust column widths
        column_widths = [25, 20, 20, 12, 40]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=route_import_template.xlsx'
        wb.save(response)
        return response

    else:
        # Create CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=route_import_template.csv'

        writer = csv.writer(response)

        # Instructions
        writer.writerow(['ROUTE BULK IMPORT TEMPLATE'])
        writer.writerow(['Instructions:'])
        writer.writerow(['1. Do not modify the column headers'])
        writer.writerow(['2. Fill data starting from the row after sample data'])
        writer.writerow(['3. Required fields: name, start_point, end_point, fare'])
        writer.writerow(['4. Fare should be a number (e.g., 500, 750.50)'])
        writer.writerow(['5. Save and upload this file'])
        writer.writerow([])  # Empty row

        # Headers
        headers = ['name', 'start_point', 'end_point', 'fare', 'note']
        writer.writerow(headers)

        # Sample data
        sample_data = ['Route 1 - Mirpur', 'Mirpur 10', 'School Campus', '500', 'Morning pickup at 7:00 AM']
        writer.writerow(sample_data)

        return response


@login_required
def bulk_route_import(request):
    """
    Handle bulk route import - upload, validate, preview, and import
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'preview')

        if action == 'preview':
            # Handle file upload and validation
            uploaded_file = request.FILES.get('route_file')

            if not uploaded_file:
                messages.error(request, 'Please select a file to upload')
                return redirect('bulk_route_import')

            # Validate file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['xlsx', 'xls', 'csv']:
                messages.error(request, 'Invalid file format. Please upload Excel (.xlsx) or CSV (.csv) file')
                return redirect('bulk_route_import')

            # Parse file based on format
            if file_extension in ['xlsx', 'xls']:
                routes_data, errors = parse_route_excel_file(uploaded_file)
            else:
                routes_data, errors = parse_route_csv_file(uploaded_file)

            if errors:
                # Show errors
                return render(request, 'student_management/transport/bulk_import_route_errors.html', {
                    'errors': errors,
                    'total_errors': len(errors),
                    'success_count': len(routes_data)
                })

            # Show preview
            return render(request, 'student_management/transport/bulk_import_route_preview.html', {
                'routes': routes_data,
                'total_count': len(routes_data)
            })

        elif action == 'import':
            # Import routes from form data
            routes_data = []
            i = 0
            while True:
                route_name = request.POST.get(f'name_{i}')
                if not route_name:
                    break

                route_data = {
                    'name': route_name,
                    'start_point': request.POST.get(f'start_point_{i}'),
                    'end_point': request.POST.get(f'end_point_{i}'),
                    'fare': request.POST.get(f'fare_{i}'),
                    'note': request.POST.get(f'note_{i}'),
                }
                routes_data.append(route_data)
                i += 1

            # Import routes
            imported_count = 0
            for route_data in routes_data:
                try:
                    # Get school from request user
                    school = request.user.institution

                    # Create route
                    TransportRoute.objects.create(
                        school=school,
                        name=route_data['name'],
                        start_point=route_data['start_point'],
                        end_point=route_data['end_point'],
                        fare=Decimal(route_data['fare']),
                        note=route_data['note'] or '',
                    )
                    imported_count += 1
                except Exception as e:
                    messages.error(request, f'Error importing route {route_data["name"]}: {str(e)}')

            messages.success(request, f'Successfully imported {imported_count} routes')
            return redirect('route_list')

    # GET request - show upload form
    return render(request, 'student_management/transport/bulk_import_route_form.html', {
        'excel_available': EXCEL_AVAILABLE
    })


def parse_route_excel_file(uploaded_file):
    """
    Parse Excel file and extract route data
    Returns: (routes_data, errors)
    """
    routes_data = []
    errors = []

    try:
        wb = openpyxl.load_workbook(uploaded_file)
        ws = wb.active

        # Find header row (should be row 8 based on template)
        header_row = None
        for row_num in range(1, 15):
            cell_value = ws.cell(row=row_num, column=1).value
            if cell_value and str(cell_value).strip().lower() == 'name':
                header_row = row_num
                break

        if not header_row:
            errors.append('Could not find header row. Please use the template format.')
            return routes_data, errors

        # Get headers
        headers = []
        for col in range(1, 6):  # 5 columns
            header = ws.cell(row=header_row, column=col).value
            headers.append(str(header).strip().lower() if header else '')

        # Process data rows
        for row_num in range(header_row + 1, ws.max_row + 1):
            # Skip sample row
            first_cell = ws.cell(row=row_num, column=1).value
            if not first_cell or str(first_cell).strip() == '':
                continue

            # Check if this is sample data row
            if 'Route 1 - Mirpur' in str(first_cell).strip():
                continue

            row_data = {}
            row_errors = []

            # Extract data from each column
            for col_idx, header in enumerate(headers, 1):
                cell_value = ws.cell(row=row_num, column=col_idx).value
                row_data[header] = str(cell_value).strip() if cell_value else ''

            # Validate required fields
            if not row_data.get('name'):
                row_errors.append(f'Row {row_num}: Route name is required')

            if not row_data.get('start_point'):
                row_errors.append(f'Row {row_num}: Start point is required')

            if not row_data.get('end_point'):
                row_errors.append(f'Row {row_num}: End point is required')

            if not row_data.get('fare'):
                row_errors.append(f'Row {row_num}: Fare is required')

            # Validate fare is a valid number
            if row_data.get('fare'):
                try:
                    row_data['fare'] = Decimal(row_data['fare'])
                    if row_data['fare'] < 0:
                        row_errors.append(f'Row {row_num}: Fare must be a positive number')
                except (ValueError, InvalidOperation):
                    row_errors.append(f'Row {row_num}: Fare must be a valid number (e.g., 500, 750.50)')

            if row_errors:
                errors.extend(row_errors)
            else:
                routes_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading Excel file: {str(e)}')

    return routes_data, errors


def parse_route_csv_file(uploaded_file):
    """
    Parse CSV file and extract route data
    Returns: (routes_data, errors)
    """
    routes_data = []
    errors = []

    try:
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(file_content))

        # Normalize header names
        fieldnames = [field.strip().lower() for field in csv_reader.fieldnames]

        # Check required headers
        if 'name' not in fieldnames or 'start_point' not in fieldnames or 'end_point' not in fieldnames or 'fare' not in fieldnames:
            errors.append('Missing required columns. Please use the template format.')
            return routes_data, errors

        row_num = 2  # Start from 2 (1 is header)

        for row in csv_reader:
            row_num += 1

            # Normalize row keys
            row_data = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}

            # Skip empty rows
            if not row_data.get('name'):
                continue

            # Skip sample data
            if 'Route 1 - Mirpur' in row_data.get('name', ''):
                continue

            row_errors = []

            # Validate required fields
            if not row_data.get('name'):
                row_errors.append(f'Row {row_num}: Route name is required')

            if not row_data.get('start_point'):
                row_errors.append(f'Row {row_num}: Start point is required')

            if not row_data.get('end_point'):
                row_errors.append(f'Row {row_num}: End point is required')

            if not row_data.get('fare'):
                row_errors.append(f'Row {row_num}: Fare is required')

            # Validate fare is a valid number
            if row_data.get('fare'):
                try:
                    row_data['fare'] = Decimal(row_data['fare'])
                    if row_data['fare'] < 0:
                        row_errors.append(f'Row {row_num}: Fare must be a positive number')
                except (ValueError, InvalidOperation):
                    row_errors.append(f'Row {row_num}: Fare must be a valid number (e.g., 500, 750.50)')

            if row_errors:
                errors.extend(row_errors)
            else:
                routes_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading CSV file: {str(e)}')

    return routes_data, errors
