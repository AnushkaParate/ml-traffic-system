from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Extra fields on top of Django's built-in User model.

    We keep django.contrib.auth.User as-is (so login/signup/admin all work
    out of the box) and attach a Profile for the fields specific to this
    project: phone number and role (normal user vs traffic admin).
    """

    ROLE_USER = 'user'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_USER, 'Registered User'),
        (ROLE_ADMIN, 'Traffic Admin'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} ({self.role})'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN


class Vehicle(models.Model):
    """A vehicle registered by a user. This is what number-plate OCR results
    get matched against when a violation is detected (see the anpr/challan
    apps)."""

    VEHICLE_TYPE_CHOICES = [
        ('two_wheeler', 'Two Wheeler'),
        ('four_wheeler', 'Four Wheeler'),
        ('other', 'Other'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles'
    )
    plate_number = models.CharField(max_length=20, unique=True, db_index=True)
    vehicle_type = models.CharField(
        max_length=20, choices=VEHICLE_TYPE_CHOICES, default='two_wheeler'
    )
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.plate_number} ({self.owner.username})'
