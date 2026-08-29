from django.db import models

from accounts.models import Vehicle


class Violation(models.Model):
    """A single detected violation event. Created by the detection/anpr
    pipeline once a helmet/triple-riding violation is confirmed and the
    plate has been OCR-matched to a registered Vehicle."""

    HELMET = 'no_helmet'
    TRIPLE_RIDING = 'triple_riding'
    VIOLATION_TYPE_CHOICES = [
        (HELMET, 'No Helmet'),
        (TRIPLE_RIDING, 'Triple Riding'),
    ]

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='violations',
        null=True, blank=True,  # null until plate OCR successfully matches
    )
    violation_type = models.CharField(max_length=20, choices=VIOLATION_TYPE_CHOICES)
    video_source = models.CharField(max_length=255, help_text='Filename of the source video/feed')
    evidence_image = models.ImageField(upload_to='violations/%Y/%m/%d/', null=True, blank=True)
    confidence_score = models.FloatField(default=0.0)
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_violation_type_display()} - {self.vehicle or "unmatched plate"}'


class Challan(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
    ]

    FINE_AMOUNTS = {
        Violation.HELMET: 500,
        Violation.TRIPLE_RIDING: 1000,
    }

    violation = models.OneToOneField(Violation, on_delete=models.CASCADE, related_name='challan')
    fine_amount = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    issued_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.fine_amount:
            self.fine_amount = self.FINE_AMOUNTS.get(self.violation.violation_type, 500)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Challan #{self.pk} - Rs.{self.fine_amount} ({self.status})'
