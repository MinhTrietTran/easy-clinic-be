from django.test import TestCase
from .models import Appointment

class AppointmentTest(TestCase):
    def test_create_appointment(self):
        apt = Appointment.objects.create(
            time_start='2025-06-24T09:00',
            status='pending',
            patient_id='...',
            doctor_id='...'
        )
        self.assertEqual(apt.status, 'pending')
