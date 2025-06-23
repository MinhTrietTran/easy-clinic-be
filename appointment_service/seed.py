import os
import django
import uuid
from datetime import datetime, timedelta, time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appointment_service.settings")
django.setup()

from appointment.models import Appointment, Schedule, Shift

# Xoá dữ liệu cũ (nếu muốn làm mới DB mỗi lần seed)
Appointment.objects.all().delete()
Schedule.objects.all().delete()
Shift.objects.all().delete()

print(" Đã xóa dữ liệu cũ.")

# Seed Shift
shift1 = Shift.objects.create(time_start=time(8, 0), time_end=time(12, 0), is_archived=False)
shift2 = Shift.objects.create(time_start=time(13, 0), time_end=time(17, 0), is_archived=False)

# Seed Schedule
schedule1 = Schedule.objects.create(time_from=time(9, 0), time_to=time(9, 30), is_active=True)
schedule2 = Schedule.objects.create(time_from=time(10, 0), time_to=time(10, 30), is_active=True)
schedule3 = Schedule.objects.create(time_from=time(11, 0), time_to=time(11, 30), is_active=True)

# Seed Appointments
now = datetime.now()

Appointment.objects.create(
    time_start=now + timedelta(days=1, hours=9),
    end_time=now + timedelta(days=1, hours=9, minutes=30),
    status='confirmed',
    amount_pay=200000,
    total_cost=300000,
    patient_id=uuid.uuid4(),
    doctor_id=uuid.uuid4(),
    schedule_id=schedule1.schedule_id,
    shift_id=shift1.shift_id
)

Appointment.objects.create(
    time_start=now + timedelta(days=2, hours=10),
    end_time=now + timedelta(days=2, hours=10, minutes=30),
    status='pending',
    amount_pay=150000,
    total_cost=250000,
    patient_id=uuid.uuid4(),
    doctor_id=uuid.uuid4(),
    schedule_id=schedule2.schedule_id,
    shift_id=shift1.shift_id
)

Appointment.objects.create(
    time_start=now + timedelta(days=3, hours=11),
    end_time=now + timedelta(days=3, hours=11, minutes=30),
    status='completed',
    amount_pay=300000,
    total_cost=300000,
    patient_id=uuid.uuid4(),
    doctor_id=uuid.uuid4(),
    schedule_id=schedule3.schedule_id,
    shift_id=shift2.shift_id
)

print(" Seed thành công dữ liệu cho Appointments, Shifts và Schedules.")
