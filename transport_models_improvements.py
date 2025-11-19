"""
Suggested improvements for Transport Management Models
Add these to your models.py file
"""

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

# Add Driver model (currently missing)
class Driver(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]

    school = models.ForeignKey(
        'Institution',
        on_delete=models.CASCADE,
        related_name='drivers'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^[0-9]{10,15}$', "Invalid phone")]
    )
    email = models.EmailField(blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_joining = models.DateField(default=timezone.now)
    photo = models.ImageField(upload_to='drivers/photos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    emergency_contact = models.CharField(max_length=15, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


# Improved Vehicle model
class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive'),
    ]

    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('cng', 'CNG'),
        ('electric', 'Electric'),
    ]

    school = models.ForeignKey(
        'Institution',
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    vehicle_number = models.CharField(max_length=20, unique=True, verbose_name="Vehicle Number/Plate")
    vehicle_model = models.CharField(max_length=100, verbose_name="Model")
    vehicle_type = models.CharField(max_length=50, default='Bus', verbose_name="Type (Bus/Van/Car)")
    capacity = models.PositiveIntegerField(verbose_name="Seating Capacity")
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_vehicles'
    )
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='diesel')
    manufacture_year = models.PositiveIntegerField(null=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    fitness_certificate_expiry = models.DateField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    next_service_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    gps_device_id = models.CharField(max_length=100, blank=True, verbose_name="GPS Device ID")
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='vehicles/photos/', blank=True, null=True)

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ['vehicle_number']

    def __str__(self):
        return f"{self.vehicle_number} - {self.vehicle_model}"

    def is_service_due(self):
        if self.next_service_date:
            return self.next_service_date <= timezone.now().date()
        return False


# Add RouteStop model for detailed route management
class RouteStop(models.Model):
    route = models.ForeignKey(
        TransportRoute,
        on_delete=models.CASCADE,
        related_name='stops'
    )
    stop_name = models.CharField(max_length=200)
    stop_order = models.PositiveIntegerField(help_text="Order in route sequence")
    pickup_time = models.TimeField(null=True, blank=True)
    drop_time = models.TimeField(null=True, blank=True)
    distance_from_school = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Distance in KM"
    )
    landmark = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['route', 'stop_order']
        unique_together = ('route', 'stop_order')

    def __str__(self):
        return f"{self.route.name} - {self.stop_name}"


# Add VehicleExpense model for tracking costs
class VehicleExpense(models.Model):
    EXPENSE_TYPES = [
        ('fuel', 'Fuel'),
        ('maintenance', 'Maintenance'),
        ('insurance', 'Insurance'),
        ('tax', 'Tax/Registration'),
        ('repair', 'Repair'),
        ('other', 'Other'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    receipt = models.FileField(upload_to='vehicle_expenses/', blank=True, null=True)
    odometer_reading = models.PositiveIntegerField(null=True, blank=True, help_text="Current KM reading")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.get_expense_type_display()} - {self.amount}"
