from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    """Landing page after login. Shows a different view for admins vs
    regular users. Right now this just confirms auth + role is working --
    Member A/C will flesh this out in Week 5 with real violation/challan
    data once the challan app has models populated."""
    is_admin = hasattr(request.user, 'profile') and request.user.profile.is_admin
    vehicles = request.user.vehicles.all() if not is_admin else []
    return render(request, 'dashboard/home.html', {
        'is_admin': is_admin,
        'vehicles': vehicles,
    })
