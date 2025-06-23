from django.db import models
import uuid

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    appointment_id = models.AutoField(primary_key=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    amount_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    patient_id = models.UUIDField()
    doctor_id = models.UUIDField()

    def __str__(self):
        return f'Appointment #{self.appointment_id} - {self.status}'


class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    time_from = models.TimeField()
    time_to = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.time_from} - {self.time_to}"


class Shift(models.Model):
    shift_id = models.AutoField(primary_key=True)
    time_start = models.TimeField()
    time_end = models.TimeField()
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"Shift {self.shift_id}"
