from django import forms

from accounts.models import Vehicle
from .models import Violation


class ManualViolationForm(forms.ModelForm):
    """Standing in for what the detection/anpr pipeline will eventually
    submit automatically. An admin looks up a plate number, picks the
    violation type, and (optionally) attaches an evidence photo.

    Once detection.py and anpr's OCR pipeline are ready, they'll call the
    same create_violation_and_challan() service function directly instead
    of going through this form -- see challan/services.py.
    """

    plate_number = forms.CharField(
        max_length=20,
        help_text="The vehicle's registered plate number, e.g. MH31AB1234",
    )

    class Meta:
        model = Violation
        fields = ['violation_type', 'evidence_image']

    def clean_plate_number(self):
        plate = self.cleaned_data['plate_number'].upper().replace(' ', '')
        try:
            self.vehicle = Vehicle.objects.get(plate_number=plate)
        except Vehicle.DoesNotExist:
            raise forms.ValidationError('No registered vehicle found with this plate number.')
        return plate