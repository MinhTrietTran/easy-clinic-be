import requests
from django.conf import settings
from datetime import datetime
from .models import Appointment
from django.db import transaction

class UserServiceClient:
    BASE_URL = settings.USER_SERVICE_URL  # e.g., "http://user-service:8000"

    @staticmethod
    def get_doctors_by_department(department):
        try:
            res = requests.get(f"{UserServiceClient.BASE_URL}/doctors/?department={department}")
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    @staticmethod
    def get_doctor_info(doctor_id):
        try:
            res = requests.get(f"{UserServiceClient.BASE_URL}/doctors/{doctor_id}")
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    @staticmethod
    def get_patient_info(patient_id):
        try:
            res = requests.get(f"{UserServiceClient.BASE_URL}/patients/{patient_id}")
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

class AppointmentService:
    @staticmethod
    @transaction.atomic
    def create_appointment(data):
        doctor_id = data.get("doctor_id")
        patient_id = data.get("patient_id")
        time_start = data.get("time_start")
        end_time = data.get("end_time")

        if not (doctor_id and patient_id and time_start and end_time):
            raise ValueError("Thiếu thông tin cần thiết để đặt lịch")

        overlap = Appointment.objects.filter(
            doctor_id=doctor_id,
            time_start__lt=end_time,
            end_time__gt=time_start
        )
        if overlap.exists():
            raise ValueError("Bác sĩ đã có lịch trong khoảng thời gian này")

        appointment = Appointment.objects.create(**data)
        return appointment

    @staticmethod
    def get_appointment_with_user_info(appointment_id):
        try:
            appointment = Appointment.objects.get(pk=appointment_id)
            doctor_info = UserServiceClient.get_doctor_info(appointment.doctor_id)
            patient_info = UserServiceClient.get_patient_info(appointment.patient_id)
            result = {
                "appointment_id": appointment.appointment_id,
                "time_start": appointment.time_start,
                "end_time": appointment.end_time,
                "status": appointment.status,
                "amount_pay": appointment.amount_pay,
                "total_cost": appointment.total_cost,
                "doctor_id": appointment.doctor_id,
                "doctor_info": doctor_info,
                "patient_id": appointment.patient_id,
                "patient_info": patient_info,
            }
            return result
        except Appointment.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def update_appointment_status(appointment_id, new_status):
        try:
            appointment = Appointment.objects.get(pk=appointment_id)
            valid_transitions = {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['in_progress', 'rescheduled', 'cancelled'],
                'in_progress': ['completed', 'no_show'],
            }
            current = appointment.status
            if current in valid_transitions and new_status in valid_transitions[current]:
                appointment.status = new_status
                appointment.save()
                return appointment
            raise ValueError(f"Không thể chuyển trạng thái từ {current} sang {new_status}")
        except Appointment.DoesNotExist:
            raise ValueError("Không tìm thấy cuộc hẹn")

    @staticmethod
    def auto_assign_doctor(department, time_start, end_time):
        # mock data nếu users chưa có
        mock_doctors = [
            {"id": "doctor-1", "name": "Dr. A"},
            {"id": "doctor-2", "name": "Dr. B"},
        ]
        doctors = UserServiceClient.get_doctors_by_department(department)
        if not doctors:
            doctors = mock_doctors

        for doctor in doctors:
            has_overlap = Appointment.objects.filter(
                doctor_id=doctor['id'],
                time_start__lt=end_time,
                end_time__gt=time_start
            ).exists()
            if not has_overlap:
                return doctor['id']
        raise ValueError("Không tìm thấy bác sĩ nào trống lịch")

    @staticmethod
    @transaction.atomic
    def reschedule_appointment(original_id, new_time_start, new_end_time):
        try:
            original = Appointment.objects.get(pk=original_id)
            original.status = 'rescheduled'
            original.save()

            new_appointment = Appointment.objects.create(
                time_start=new_time_start,
                end_time=new_end_time,
                status='pending',
                amount_pay=original.amount_pay,
                total_cost=original.total_cost,
                patient_id=original.patient_id,
                doctor_id=original.doctor_id,
                schedule=original.schedule,
                shift=original.shift
            )
            return new_appointment
        except Appointment.DoesNotExist:
            raise ValueError("Không tìm thấy lịch cũ để reschedule")