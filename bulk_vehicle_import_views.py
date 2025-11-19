"""
Bulk Vehicle Import Views
Add these functions to your student_management/views.py

Features:
- Download formatted Excel/CSV template for bulk vehicle import
- Upload and validate vehicle data
- Preview vehicles before importing
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

from .models import Vehicle


@login_required
def download_vehicle_import_template(request):
    """
    Generate and download Excel or CSV template for bulk vehicle import
    """
    file_format = request.GET.get('format', 'excel').lower()

    if file_format == 'excel' and EXCEL_AVAILABLE:
        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Vehicle Import"

        # Instructions (rows 1-8)
        instructions = [
            "VEHICLE BULK IMPORT TEMPLATE",
            "Instructions:",
            "1. Do not modify the column headers (row 9)",
            "2. Fill data starting from row 11 (row 10 is a sample - delete it before upload)",
            "3. Required fields: vehicle_number, vehicle_model, capacity",
            "4. Valid status: active, maintenance, inactive",
            "5. Valid fuel_type: petrol, diesel, cng, electric",
            "6. Save and upload this file",
        ]

        for i, instruction in enumerate(instructions, 1):
            cell = ws.cell(row=i, column=1, value=instruction)
            cell.font = Font(bold=True, color='FF0000', size=11)

        # Headers (row 9)
        headers = [
            'vehicle_number',           # Required - unique (e.g., DH-12-3456)
            'vehicle_model',            # Required - model name
            'vehicle_type',             # Optional - Bus/Van/Car (default: Bus)
            'capacity',                 # Required - integer (seating capacity)
            'fuel_type',                # Optional - petrol/diesel/cng/electric
            'manufacture_year',         # Optional - integer (e.g., 2020)
            'registration_date',        # Optional - YYYY-MM-DD
            'insurance_expiry',         # Optional - YYYY-MM-DD
            'fitness_certificate_expiry',# Optional - YYYY-MM-DD
            'last_service_date',        # Optional - YYYY-MM-DD
            'next_service_date',        # Optional - YYYY-MM-DD
            'status',                   # Optional - active/maintenance/inactive
            'gps_device_id',            # Optional - GPS tracker ID
            'notes',                    # Optional - text
        ]

        header_row = 9
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col, value=header)
            cell.font = Font(bold=True, color='FFFFFF', size=11)
            cell.fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Sample data (row 10)
        sample_data = [
            'DH-12-3456',                           # vehicle_number
            'Tata LP 909',                          # vehicle_model
            'Bus',                                  # vehicle_type
            '45',                                   # capacity
            'diesel',                               # fuel_type
            '2020',                                 # manufacture_year
            date.today().strftime('%Y-%m-%d'),      # registration_date
            (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),  # insurance_expiry
            (date.today() + timedelta(days=180)).strftime('%Y-%m-%d'),  # fitness_certificate_expiry
            date.today().strftime('%Y-%m-%d'),      # last_service_date
            (date.today() + timedelta(days=90)).strftime('%Y-%m-%d'),   # next_service_date
            'active',                               # status
            'GPS-001',                              # gps_device_id
            'School bus for Route 1',               # notes
        ]

        sample_row = 10
        for col, value in enumerate(sample_data, 1):
            cell = ws.cell(row=sample_row, column=col, value=value)
            cell.font = Font(italic=True, color='808080')

        # Adjust column widths
        column_widths = [18, 18, 15, 10, 12, 16, 16, 16, 24, 18, 18, 15, 15, 30]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=vehicle_import_template.xlsx'
        wb.save(response)
        return response

    else:
        # Create CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=vehicle_import_template.csv'

        writer = csv.writer(response)

        # Instructions
        writer.writerow(['VEHICLE BULK IMPORT TEMPLATE'])
        writer.writerow(['Instructions:'])
        writer.writerow(['1. Do not modify the column headers'])
        writer.writerow(['2. Fill data starting from the row after sample data'])
        writer.writerow(['3. Required fields: vehicle_number, vehicle_model, capacity'])
        writer.writerow(['4. Valid status: active, maintenance, inactive'])
        writer.writerow(['5. Valid fuel_type: petrol, diesel, cng, electric'])
        writer.writerow(['6. Save and upload this file'])
        writer.writerow([])  # Empty row

        # Headers
        headers = [
            'vehicle_number', 'vehicle_model', 'vehicle_type', 'capacity', 'fuel_type',
            'manufacture_year', 'registration_date', 'insurance_expiry',
            'fitness_certificate_expiry', 'last_service_date', 'next_service_date',
            'status', 'gps_device_id', 'notes'
        ]
        writer.writerow(headers)

        # Sample data
        sample_data = [
            'DH-12-3456', 'Tata LP 909', 'Bus', '45', 'diesel', '2020',
            date.today().strftime('%Y-%m-%d'),
            (date.today() + timedelta(days=365)).strftime('%Y-%m-%d'),
            (date.today() + timedelta(days=180)).strftime('%Y-%m-%d'),
            date.today().strftime('%Y-%m-%d'),
            (date.today() + timedelta(days=90)).strftime('%Y-%m-%d'),
            'active', 'GPS-001', 'School bus for Route 1'
        ]
        writer.writerow(sample_data)

        return response


@login_required
def bulk_vehicle_import(request):
    """
    Handle bulk vehicle import - upload, validate, preview, and import
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'preview')

        if action == 'preview':
            # Handle file upload and validation
            uploaded_file = request.FILES.get('vehicle_file')

            if not uploaded_file:
                messages.error(request, 'Please select a file to upload')
                return redirect('bulk_vehicle_import')

            # Validate file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension not in ['xlsx', 'xls', 'csv']:
                messages.error(request, 'Invalid file format. Please upload Excel (.xlsx) or CSV (.csv) file')
                return redirect('bulk_vehicle_import')

            # Parse file based on format
            if file_extension in ['xlsx', 'xls']:
                vehicles_data, errors = parse_vehicle_excel_file(uploaded_file)
            else:
                vehicles_data, errors = parse_vehicle_csv_file(uploaded_file)

            if errors:
                # Show errors
                return render(request, 'student_management/transport/bulk_import_vehicle_errors.html', {
                    'errors': errors,
                    'total_errors': len(errors),
                    'success_count': len(vehicles_data)
                })

            # Show preview
            return render(request, 'student_management/transport/bulk_import_vehicle_preview.html', {
                'vehicles': vehicles_data,
                'total_count': len(vehicles_data)
            })

        elif action == 'import':
            # Import vehicles from form data
            vehicles_data = []
            i = 0
            while True:
                vehicle_number = request.POST.get(f'vehicle_number_{i}')
                if not vehicle_number:
                    break

                vehicle_data = {
                    'vehicle_number': vehicle_number,
                    'vehicle_model': request.POST.get(f'vehicle_model_{i}'),
                    'vehicle_type': request.POST.get(f'vehicle_type_{i}'),
                    'capacity': request.POST.get(f'capacity_{i}'),
                    'fuel_type': request.POST.get(f'fuel_type_{i}'),
                    'manufacture_year': request.POST.get(f'manufacture_year_{i}'),
                    'registration_date': request.POST.get(f'registration_date_{i}'),
                    'insurance_expiry': request.POST.get(f'insurance_expiry_{i}'),
                    'fitness_certificate_expiry': request.POST.get(f'fitness_certificate_expiry_{i}'),
                    'last_service_date': request.POST.get(f'last_service_date_{i}'),
                    'next_service_date': request.POST.get(f'next_service_date_{i}'),
                    'status': request.POST.get(f'status_{i}'),
                    'gps_device_id': request.POST.get(f'gps_device_id_{i}'),
                    'notes': request.POST.get(f'notes_{i}'),
                }
                vehicles_data.append(vehicle_data)
                i += 1

            # Import vehicles
            imported_count = 0
            for vehicle_data in vehicles_data:
                try:
                    # Get school from request user
                    school = request.user.institution

                    # Create vehicle
                    Vehicle.objects.create(
                        school=school,
                        vehicle_number=vehicle_data['vehicle_number'],
                        vehicle_model=vehicle_data['vehicle_model'],
                        vehicle_type=vehicle_data['vehicle_type'] or 'Bus',
                        capacity=int(vehicle_data['capacity']),
                        fuel_type=vehicle_data['fuel_type'] or 'diesel',
                        manufacture_year=int(vehicle_data['manufacture_year']) if vehicle_data['manufacture_year'] else None,
                        registration_date=vehicle_data['registration_date'] or None,
                        insurance_expiry=vehicle_data['insurance_expiry'] or None,
                        fitness_certificate_expiry=vehicle_data['fitness_certificate_expiry'] or None,
                        last_service_date=vehicle_data['last_service_date'] or None,
                        next_service_date=vehicle_data['next_service_date'] or None,
                        status=vehicle_data['status'] or 'active',
                        gps_device_id=vehicle_data['gps_device_id'] or '',
                        notes=vehicle_data['notes'] or '',
                    )
                    imported_count += 1
                except Exception as e:
                    messages.error(request, f'Error importing vehicle {vehicle_data["vehicle_number"]}: {str(e)}')

            messages.success(request, f'Successfully imported {imported_count} vehicles')
            return redirect('vehicle_list')

    # GET request - show upload form
    return render(request, 'student_management/transport/bulk_import_vehicle_form.html', {
        'excel_available': EXCEL_AVAILABLE
    })


def parse_vehicle_excel_file(uploaded_file):
    """
    Parse Excel file and extract vehicle data
    Returns: (vehicles_data, errors)
    """
    vehicles_data = []
    errors = []

    try:
        wb = openpyxl.load_workbook(uploaded_file)
        ws = wb.active

        # Find header row (should be row 9 based on template)
        header_row = None
        for row_num in range(1, 15):
            cell_value = ws.cell(row=row_num, column=1).value
            if cell_value and str(cell_value).strip().lower() == 'vehicle_number':
                header_row = row_num
                break

        if not header_row:
            errors.append('Could not find header row. Please use the template format.')
            return vehicles_data, errors

        # Get headers
        headers = []
        for col in range(1, 15):  # 14 columns
            header = ws.cell(row=header_row, column=col).value
            headers.append(str(header).strip().lower() if header else '')

        # Process data rows
        for row_num in range(header_row + 1, ws.max_row + 1):
            # Skip sample row
            first_cell = ws.cell(row=row_num, column=1).value
            if not first_cell or str(first_cell).strip() == '':
                continue

            # Check if this is sample data row
            if str(first_cell).strip().upper() == 'DH-12-3456':
                continue

            row_data = {}
            row_errors = []

            # Extract data from each column
            for col_idx, header in enumerate(headers, 1):
                cell_value = ws.cell(row=row_num, column=col_idx).value
                row_data[header] = str(cell_value).strip() if cell_value else ''

            # Validate required fields
            if not row_data.get('vehicle_number'):
                row_errors.append(f'Row {row_num}: Vehicle number is required')

            if not row_data.get('vehicle_model'):
                row_errors.append(f'Row {row_num}: Vehicle model is required')

            if not row_data.get('capacity'):
                row_errors.append(f'Row {row_num}: Capacity is required')

            # Validate vehicle_number uniqueness
            if row_data.get('vehicle_number'):
                if Vehicle.objects.filter(vehicle_number=row_data['vehicle_number']).exists():
                    row_errors.append(f'Row {row_num}: Vehicle number {row_data["vehicle_number"]} already exists')

            # Validate status
            if row_data.get('status'):
                if row_data['status'].lower() not in ['active', 'maintenance', 'inactive', '']:
                    row_errors.append(f'Row {row_num}: Invalid status. Use: active, maintenance, or inactive')

            # Validate fuel_type
            if row_data.get('fuel_type'):
                if row_data['fuel_type'].lower() not in ['petrol', 'diesel', 'cng', 'electric', '']:
                    row_errors.append(f'Row {row_num}: Invalid fuel_type. Use: petrol, diesel, cng, or electric')

            # Validate integer fields
            int_fields = ['capacity', 'manufacture_year']
            for field in int_fields:
                if row_data.get(field):
                    try:
                        row_data[field] = int(float(row_data[field]))
                    except (ValueError, InvalidOperation):
                        row_errors.append(f'Row {row_num}: {field} must be a valid integer')

            # Validate dates
            date_fields = ['registration_date', 'insurance_expiry', 'fitness_certificate_expiry',
                          'last_service_date', 'next_service_date']
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
                vehicles_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading Excel file: {str(e)}')

    return vehicles_data, errors


def parse_vehicle_csv_file(uploaded_file):
    """
    Parse CSV file and extract vehicle data
    Returns: (vehicles_data, errors)
    """
    vehicles_data = []
    errors = []

    try:
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(file_content))

        # Normalize header names
        fieldnames = [field.strip().lower() for field in csv_reader.fieldnames]

        # Check required headers
        if 'vehicle_number' not in fieldnames or 'vehicle_model' not in fieldnames or 'capacity' not in fieldnames:
            errors.append('Missing required columns. Please use the template format.')
            return vehicles_data, errors

        row_num = 2  # Start from 2 (1 is header)

        for row in csv_reader:
            row_num += 1

            # Normalize row keys
            row_data = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}

            # Skip empty rows
            if not row_data.get('vehicle_number'):
                continue

            # Skip sample data
            if row_data.get('vehicle_number').upper() == 'DH-12-3456':
                continue

            row_errors = []

            # Validate required fields
            if not row_data.get('vehicle_number'):
                row_errors.append(f'Row {row_num}: Vehicle number is required')

            if not row_data.get('vehicle_model'):
                row_errors.append(f'Row {row_num}: Vehicle model is required')

            if not row_data.get('capacity'):
                row_errors.append(f'Row {row_num}: Capacity is required')

            # Validate vehicle_number uniqueness
            if row_data.get('vehicle_number'):
                if Vehicle.objects.filter(vehicle_number=row_data['vehicle_number']).exists():
                    row_errors.append(f'Row {row_num}: Vehicle number {row_data["vehicle_number"]} already exists')

            # Validate status
            if row_data.get('status'):
                if row_data['status'].lower() not in ['active', 'maintenance', 'inactive', '']:
                    row_errors.append(f'Row {row_num}: Invalid status. Use: active, maintenance, or inactive')

            # Validate fuel_type
            if row_data.get('fuel_type'):
                if row_data['fuel_type'].lower() not in ['petrol', 'diesel', 'cng', 'electric', '']:
                    row_errors.append(f'Row {row_num}: Invalid fuel_type. Use: petrol, diesel, cng, or electric')

            # Validate integer fields
            int_fields = ['capacity', 'manufacture_year']
            for field in int_fields:
                if row_data.get(field):
                    try:
                        row_data[field] = int(float(row_data[field]))
                    except (ValueError, InvalidOperation):
                        row_errors.append(f'Row {row_num}: {field} must be a valid integer')

            # Validate dates
            date_fields = ['registration_date', 'insurance_expiry', 'fitness_certificate_expiry',
                          'last_service_date', 'next_service_date']
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
                vehicles_data.append(row_data)

    except Exception as e:
        errors.append(f'Error reading CSV file: {str(e)}')

    return vehicles_data, errors
