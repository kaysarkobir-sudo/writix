"""
Updated dashboard view to include Transport Management statistics
Add this to your views.py file (or update your existing dashboard view)
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from student_management.models import (
    Vehicle, TransportRoute, TransportMember,
    Student, Teacher, AcademicClass
)

@login_required
def main_dashboard(request):
    """
    Main dashboard view with statistics for all modules
    """

    # Get user's institution
    institution = None
    if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'institution'):
        institution = request.user.profile.institution

    # Transport Statistics
    if institution:
        total_buses = Vehicle.objects.filter(school=institution).count()
        total_routes = TransportRoute.objects.filter(school=institution).count()
        total_transport_members = TransportMember.objects.filter(school=institution).count()
    else:
        total_buses = Vehicle.objects.count()
        total_routes = TransportRoute.objects.count()
        total_transport_members = TransportMember.objects.count()

    # Student Statistics (example - adjust based on your models)
    total_students = Student.objects.filter(institution=institution).count() if institution else Student.objects.count()

    # Teacher Statistics (example - adjust based on your models)
    total_teachers = Teacher.objects.filter(institution=institution).count() if institution else Teacher.objects.count()

    # Academic Statistics (example)
    total_classes = AcademicClass.objects.filter(institution=institution).count() if institution else AcademicClass.objects.count()

    context = {
        # Transport
        'total_buses': total_buses,
        'total_routes': total_routes,
        'total_transport_members': total_transport_members,

        # Students
        'total_students': total_students,

        # Teachers
        'total_teachers': total_teachers,

        # Academic
        'total_classes': total_classes,

        # Add more statistics as needed
    }

    return render(request, 'dashboard.html', context)


# Alternative: If you already have a dashboard view, just add these lines to it:
"""
# In your existing dashboard view, add:

from student_management.models import Vehicle, TransportRoute, TransportMember

# Get transport statistics
institution = getattr(getattr(request.user, 'profile', None), 'institution', None)

if institution:
    total_buses = Vehicle.objects.filter(school=institution).count()
    total_routes = TransportRoute.objects.filter(school=institution).count()
    total_transport_members = TransportMember.objects.filter(school=institution).count()
else:
    total_buses = Vehicle.objects.count()
    total_routes = TransportRoute.objects.count()
    total_transport_members = TransportMember.objects.count()

# Add to context
context.update({
    'total_buses': total_buses,
    'total_routes': total_routes,
    'total_transport_members': total_transport_members,
})
"""
