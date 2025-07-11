from django.db import models

class Appointment(models.Model):
    appointment_id = models.CharField(max_length=100, unique=True)
    patient_email = models.EmailField()
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment {self.appointment_id} for {self.patient_email}"

class Prescription(models.Model):
    prescription_id = models.CharField(max_length=100, unique=True)
    patient_email = models.EmailField()
    medication = models.CharField(max_length=200)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"Prescription {self.prescription_id} for {self.patient_email}"