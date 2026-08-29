from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from challan.models import Challan


@login_required
def home(request):
    is_admin = hasattr(request.user, 'profile') and request.user.profile.is_admin

    if is_admin:
        recent_challans = Challan.objects.select_related(
            'violation', 'violation__vehicle', 'violation__vehicle__owner'
        ).order_by('-issued_at')[:10]
        return render(request, 'dashboard/home.html', {
            'is_admin': True,
            'recent_challans': recent_challans,
            'total_challans': Challan.objects.count(),
            'pending_challans': Challan.objects.filter(status=Challan.STATUS_PENDING).count(),
        })

    vehicles = request.user.vehicles.all()
    challans = Challan.objects.filter(
        violation__vehicle__owner=request.user
    ).select_related('violation').order_by('-issued_at')
    return render(request, 'dashboard/home.html', {
        'is_admin': False,
        'vehicles': vehicles,
        'challans': challans,
    })