from django.db import models
import uuid


class Shift(models.Model):
    """Ca làm việc (sáng, chiều, tối...)"""
    shift_id = models.AutoField(primary_key=True)
    time_start = models.TimeField()
    time_end = models.TimeField()
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return f"Shift {self.time_start} - {self.time_end}"


class Schedule(models.Model):
    """Khoảng thời gian cụ thể có thể đặt lịch trong ngày"""
    schedule_id = models.AutoField(primary_key=True)
    time_from = models.TimeField()
    time_to = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.time_from.strftime('%H:%M')} - {self.time_to.strftime('%H:%M')}"


class Appointment(models.Model):
    """Lịch hẹn giữa bệnh nhân và bác sĩ"""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        RESCHEDULED = 'rescheduled', 'Rescheduled'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        NO_SHOW = 'no_show', 'No Show'

    appointment_id = models.AutoField(primary_key=True)
    time_created = models.DateTimeField(auto_now_add=True)

    time_start = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    amount_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Đổi từ UUIDField sang IntegerField cho patient_id và doctor_id
    patient_id = models.IntegerField()
    doctor_id = models.CharField(max_length=255, null=True, blank=True)  # Cho phép null

    # liên kết với ca hoặc khung giờ
    schedule = models.ForeignKey('Schedule', on_delete=models.SET_NULL, null=True, blank=True)
    shift = models.ForeignKey('Shift', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f'Appointment #{self.appointment_id} - {self.status}'
