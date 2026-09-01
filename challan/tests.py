from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from accounts.models import Profile, Vehicle
from .models import Challan, Violation
from .services import create_violation_and_challan


class CreateViolationAndChallanTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('vehicleowner', 'owner@example.com', 'pass12345')
        Profile.objects.create(user=self.owner, role=Profile.ROLE_USER)
        self.vehicle = Vehicle.objects.create(
            owner=self.owner, plate_number='MH31AB1234', vehicle_type='two_wheeler'
        )

    def test_creates_violation_and_challan_with_correct_fine(self):
        challan = create_violation_and_challan(self.vehicle, Violation.HELMET)
        self.assertEqual(challan.fine_amount, Challan.FINE_AMOUNTS[Violation.HELMET])
        self.assertEqual(challan.status, Challan.STATUS_PENDING)
        self.assertEqual(challan.violation.vehicle, self.vehicle)

    def test_triple_riding_fine_is_higher_than_helmet(self):
        helmet_challan = create_violation_and_challan(self.vehicle, Violation.HELMET)
        triple_challan = create_violation_and_challan(self.vehicle, Violation.TRIPLE_RIDING)
        self.assertGreater(triple_challan.fine_amount, helmet_challan.fine_amount)

    def test_email_sent_with_pdf_attachment(self):
        create_violation_and_challan(self.vehicle, Violation.HELMET)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, [self.owner.email])
        self.assertEqual(len(sent.attachments), 1)
        filename, content, mimetype = sent.attachments[0]
        self.assertTrue(filename.endswith('.pdf'))
        self.assertEqual(mimetype, 'application/pdf')

    def test_email_sent_flag_set_after_sending(self):
        challan = create_violation_and_challan(self.vehicle, Violation.HELMET)
        challan.refresh_from_db()
        self.assertTrue(challan.email_sent)


class MarkAsPaidTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('vehicleowner', 'owner@example.com', 'pass12345')
        Profile.objects.create(user=self.owner, role=Profile.ROLE_USER)
        self.other_user = User.objects.create_user('someoneelse', 'other@example.com', 'pass12345')
        Profile.objects.create(user=self.other_user, role=Profile.ROLE_USER)
        self.vehicle = Vehicle.objects.create(
            owner=self.owner, plate_number='MH31AB1234', vehicle_type='two_wheeler'
        )
        self.challan = create_violation_and_challan(self.vehicle, Violation.HELMET)

    def test_owner_can_mark_own_challan_as_paid(self):
        self.client.force_login(self.owner)
        self.client.post(f'/challan/{self.challan.pk}/pay/')
        self.challan.refresh_from_db()
        self.assertEqual(self.challan.status, Challan.STATUS_PAID)

    def test_other_user_cannot_pay_someone_elses_challan(self):
        self.client.force_login(self.other_user)
        response = self.client.post(f'/challan/{self.challan.pk}/pay/')
        self.assertEqual(response.status_code, 403)
        self.challan.refresh_from_db()
        self.assertEqual(self.challan.status, Challan.STATUS_PENDING)