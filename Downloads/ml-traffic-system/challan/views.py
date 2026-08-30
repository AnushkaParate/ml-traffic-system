from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import admin_required
from .forms import ManualViolationForm
from .models import Challan
from .pdf import generate_challan_pdf
from .services import create_violation_and_challan


@admin_required
def report_violation(request):
    if request.method == 'POST':
        form = ManualViolationForm(request.POST, request.FILES)
        if form.is_valid():
            challan = create_violation_and_challan(
                vehicle=form.vehicle,
                violation_type=form.cleaned_data['violation_type'],
                evidence_image=form.cleaned_data.get('evidence_image'),
            )
            messages.success(
                request,
                f'Challan #{challan.pk} created for {form.vehicle.plate_number} '
                f'(Rs. {challan.fine_amount}). Email sent to {form.vehicle.owner.email}.'
            )
            return redirect(reverse('dashboard:home'))
    else:
        form = ManualViolationForm()
    return render(request, 'challan/report_violation.html', {'form': form})


@login_required
def download_challan_pdf(request, challan_id):
    challan = get_object_or_404(Challan, pk=challan_id)
    is_admin = hasattr(request.user, 'profile') and request.user.profile.is_admin
    is_owner = challan.violation.vehicle.owner_id == request.user.id
    if not (is_admin or is_owner):
        return HttpResponseForbidden("You don't have permission to view this challan.")

    pdf_bytes = generate_challan_pdf(challan)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="challan_{challan.pk}.pdf"'
    return response


@login_required
def mark_as_paid(request, challan_id):
    """Mock payment -- no real gateway. Swap this for a Razorpay/Stripe
    callback in a real deployment."""
    challan = get_object_or_404(Challan, pk=challan_id)
    is_owner = challan.violation.vehicle.owner_id == request.user.id
    if not is_owner:
        return HttpResponseForbidden("You can only pay your own challans.")

    if request.method == 'POST':
        challan.status = Challan.STATUS_PAID
        challan.save(update_fields=['status'])
        messages.success(request, f'Challan #{challan.pk} marked as paid.')
    return redirect(reverse('dashboard:home'))


@admin_required
def all_challans(request):
    queryset = Challan.objects.select_related(
        'violation', 'violation__vehicle', 'violation__vehicle__owner'
    ).order_by('-issued_at')

    search = request.GET.get('q', '').strip().upper()
    if search:
        queryset = queryset.filter(violation__vehicle__plate_number__icontains=search)

    status = request.GET.get('status', '')
    if status in (Challan.STATUS_PENDING, Challan.STATUS_PAID):
        queryset = queryset.filter(status=status)

    return render(request, 'challan/all_challans.html', {
        'challans': queryset, 'search': search, 'status': status,
    })