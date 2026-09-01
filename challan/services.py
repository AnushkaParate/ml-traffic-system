"""Core business logic for turning a detected violation into a challan and
notifying the vehicle owner. Kept separate from views.py so that both the
manual admin form (views.py) AND the future automated detection pipeline
(detection/anpr apps, Week 3-4) can call the exact same function and get
identical behaviour.
"""

from django.conf import settings
from django.core.mail import EmailMessage

from .models import Challan, Violation
from .pdf import generate_challan_pdf


def create_violation_and_challan(vehicle, violation_type, video_source='manual-entry',
                                   evidence_image=None, confidence_score=1.0):
    """Create a Violation + its Challan, then email the vehicle owner with
    a PDF copy of the challan attached.

    Returns the created Challan instance. This is the single entry point
    detection code should call once it has: (1) confirmed a violation
    happened, and (2) matched a plate number to a registered Vehicle.
    """
    violation = Violation.objects.create(
        vehicle=vehicle,
        violation_type=violation_type,
        video_source=video_source,
        evidence_image=evidence_image,
        confidence_score=confidence_score,
    )

    fine_amount = Challan.FINE_AMOUNTS.get(violation_type, 500)
    challan = Challan.objects.create(violation=violation, fine_amount=fine_amount)

    _send_challan_email(challan)
    return challan


def _send_challan_email(challan):
    vehicle = challan.violation.vehicle
    owner_email = vehicle.owner.email
    if not owner_email:
        return  # nothing to send to -- shouldn't happen since signup requires email

    subject = f'E-Challan Issued - {vehicle.plate_number}'
    body = (
        f'Dear {vehicle.owner.username},\n\n'
        f'A traffic violation has been recorded against your vehicle {vehicle.plate_number}.\n\n'
        f'Violation: {challan.violation.get_violation_type_display()}\n'
        f'Fine amount: Rs. {challan.fine_amount}\n\n'
        f'Your e-challan is attached as a PDF. Please log in to the Traffic '
        f'Management System to view details and pay your fine.\n'
    )

    email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [owner_email])
    pdf_bytes = generate_challan_pdf(challan)
    email.attach(f'challan_{challan.pk}.pdf', pdf_bytes, 'application/pdf')
    email.send(fail_silently=False)

    challan.email_sent = True
    challan.save(update_fields=['email_sent'])