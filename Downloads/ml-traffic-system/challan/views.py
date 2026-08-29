from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from accounts.decorators import admin_required
from .forms import ManualViolationForm
from .services import create_violation_and_challan


@admin_required
def report_violation(request):
    """Admin-only form to manually log a violation -- this is the
    placeholder for what detection.py + anpr will eventually submit
    automatically once YOLOv8 + OCR are wired in (Week 3-4)."""
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