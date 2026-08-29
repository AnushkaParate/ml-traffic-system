from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile, Vehicle


class SignUpForm(UserCreationForm):
    """Signup form for regular users. Also creates their first vehicle
    registration in the same step, since number-plate matching needs at
    least one registered vehicle per user."""

    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    plate_number = forms.CharField(
        max_length=20,
        required=True,
        help_text='Your vehicle registration/number plate, e.g. MH31AB1234',
    )
    vehicle_type = forms.ChoiceField(choices=Vehicle.VEHICLE_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password1', 'password2']

    def clean_plate_number(self):
        plate = self.cleaned_data['plate_number'].upper().replace(' ', '')
        if Vehicle.objects.filter(plate_number=plate).exists():
            raise forms.ValidationError('This vehicle is already registered.')
        return plate

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                role=Profile.ROLE_USER,
            )
            Vehicle.objects.create(
                owner=user,
                plate_number=self.cleaned_data['plate_number'],
                vehicle_type=self.cleaned_data['vehicle_type'],
            )
        return user


class AdminSignUpForm(UserCreationForm):
    """Separate signup form for traffic admins (no vehicle registration
    needed). Keep this behind an invite code or manual approval in a real
    deployment -- for now it's open so the team can create admin accounts
    for testing."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.is_staff = True
            user.save()
            Profile.objects.create(user=user, role=Profile.ROLE_ADMIN)
        return user
