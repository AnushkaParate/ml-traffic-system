from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import SignUpForm
from .models import Profile, Vehicle


class SignUpFormTests(TestCase):
    def test_valid_signup_creates_user_profile_and_vehicle(self):
        form = SignUpForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_number': '9876543210',
            'plate_number': 'MH31AB1234',
            'vehicle_type': 'two_wheeler',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(Profile.objects.get(user=user).role, Profile.ROLE_USER)
        self.assertEqual(Vehicle.objects.get(owner=user).plate_number, 'MH31AB1234')

    def test_duplicate_plate_number_rejected(self):
        owner = User.objects.create_user('existing', 'e@example.com', 'pass12345')
        Vehicle.objects.create(owner=owner, plate_number='MH31AB1234', vehicle_type='two_wheeler')

        form = SignUpForm(data={
            'username': 'testuser2', 'email': 'test2@example.com', 'phone_number': '9876543210',
            'plate_number': 'MH31AB1234', 'vehicle_type': 'two_wheeler',
            'password1': 'ComplexPass123!', 'password2': 'ComplexPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('plate_number', form.errors)


class RoleAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('regularuser', 'u@example.com', 'pass12345')
        Profile.objects.create(user=self.user, role=Profile.ROLE_USER)

        self.admin = User.objects.create_user('adminuser', 'a@example.com', 'pass12345')
        Profile.objects.create(user=self.admin, role=Profile.ROLE_ADMIN)

    def test_regular_user_cannot_access_report_violation(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('challan:report_violation'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_report_violation(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('challan:report_violation'))
        self.assertEqual(response.status_code, 200)

    def test_logged_out_user_redirected_to_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('dashboard:home')}")