from appointment_service.service_discovery import get_service_address
import requests
from django.conf import settings
from datetime import datetime, timedelta
from ..models import Appointment
from django.db import transaction
import threading

class UserServiceClient:
    @staticmethod
    def get_base_url():
        address, port = get_service_address("user_service")
        return f"http://{address}:{port}"

    @staticmethod
    def get_doctors_by_department(department):
        try:
            base_url = UserServiceClient.get_base_url()
            res = requests.get(f"{base_url}/api/v1/users/doctors/?department={department}")
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    @staticmethod
    def get_doctor_info(doctor_id):
        try:
            base_url = UserServiceClient.get_base_url()
            res = requests.get(f"{base_url}/api/v1/users/doctors/{doctor_id}/")
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    @staticmethod
    def get_patient_info(patient_id):
        try:
            base_url = UserServiceClient.get_base_url()
            res = requests.get(f"{base_url}/api/v1/users/patients/{patient_id}/")
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    @staticmethod
    def get_patient_id_from_token(access_token):
        """
        Gọi user_service để lấy patient_id từ token
        """
        try:
            base_url = UserServiceClient.get_base_url()
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            res = requests.get(f"{base_url}/api/v1/users/patient/me/id/", headers=headers)
            if res.status_code == 200:
                return res.json()
            elif res.status_code == 403:
                return {"error": "User is not a patient"}
            elif res.status_code == 404:
                return {"error": "Patient profile not found"}
        except Exception as e:
            return {"error": f"Failed to get patient ID: {str(e)}"}
        return None

class AppointmentService:
    @staticmethod
    @transaction.atomic
    def create_appointment(data):
        """
        Tạo appointment với status pending, trả về ngay cho FE
        Sau đó xử lý assign doctor bất đồng bộ
        """
        # 1. Lấy dữ liệu đầu vào
        token = data.get("token")
        department = data.get("department")
        time_start = data.get("time_start")
        end_time = data.get("end_time")
        
        if not all([token, department, time_start]):
            raise ValueError("Thiếu thông tin cần thiết: token, department, time_start")
        
        # 2. Parse time_start và tính end_time nếu không có
        if isinstance(time_start, str):
            time_start = datetime.fromisoformat(time_start.replace('Z', '+00:00'))
        
        if not end_time:
            end_time = time_start + timedelta(minutes=30)
        elif isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # 3. Lấy thông tin patient từ token
        patient_result = UserServiceClient.get_patient_id_from_token(token)
        if not patient_result or "error" in patient_result:
            raise ValueError(f"Lỗi xác thực bệnh nhân: {patient_result.get('error', 'Token không hợp lệ')}")
        
        patient_id = patient_result.get("patient_id")
        if not patient_id:
            raise ValueError("Không thể lấy patient_id từ token")
        
        # 4. Lấy thông tin chi tiết patient
        patient_info = UserServiceClient.get_patient_info(patient_id)
        if not patient_info:
            raise ValueError("Không thể lấy thông tin chi tiết của bệnh nhân")
        
        # 5. Tạo appointment với status pending
        appointment_data = {
            "patient_id": patient_id,
            "time_start": time_start,
            "end_time": end_time,
            "status": "pending",
            "amount_pay": 0,
            "total_cost": 0,
            "doctor_id": None
        }
        
        appointment = Appointment.objects.create(**appointment_data)
        
        # 6. Trả về ngay cho FE
        result = {
            "appointment_id": str(appointment.appointment_id),
            "time_created": appointment.time_created,
            "time_start": appointment.time_start,
            "end_time": appointment.end_time,
            "status": appointment.status,
            "status_display": appointment.get_status_display(),
            "amount_pay": appointment.amount_pay,
            "total_cost": appointment.total_cost,
            "patient_id": appointment.patient_id,
            "patient_info": patient_info,
            "doctor_id": None,
            "doctor_info": None,
            "department_requested": department,
            "message": "Appointment created successfully. Doctor assignment in progress..."
        }
        
        # 7. Xử lý assign doctor bất đồng bộ
        threading.Thread(
            target=AppointmentService._process_doctor_assignment,
            args=(appointment.appointment_id, department),
            daemon=True
        ).start()
        
        return result

    @staticmethod
    def _process_doctor_assignment(appointment_id, department):
        """
        Background task để assign doctor
        """
        try:
            import time
            time.sleep(2)  # Giả lập xử lý
            
            # Lấy appointment
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            
            if appointment.status != "pending":
                return  # Đã được xử lý rồi
            
            # Auto assign doctor
            doctor_result = AppointmentService.auto_assign_doctor(
                department, 
                appointment.time_start, 
                appointment.end_time
            )
            
            doctor_id = doctor_result["doctor_id"]
            doctor_info = doctor_result["doctor_info"]
            
            # Kiểm tra overlap
            overlap = Appointment.objects.filter(
                doctor_id=doctor_id,
                time_start__lt=appointment.end_time,
                end_time__gt=appointment.time_start
            ).exclude(appointment_id=appointment_id)
            
            if overlap.exists():
                print(f"Doctor conflict for appointment {appointment_id}")
                return
            
            # Tính total_cost = doctor cost * 110%
            doctor_cost = doctor_info.get("cost", 0)
            total_cost = int(doctor_cost * 1.1) if doctor_cost else 0
            
            # Update appointment
            appointment.doctor_id = doctor_id
            appointment.status = "confirmed"
            appointment.total_cost = total_cost
            appointment.save()
            
            print(f"Doctor assigned successfully for appointment {appointment_id}")
            
        except Exception as e:
            print(f"Error assigning doctor for appointment {appointment_id}: {str(e)}")

    @staticmethod
    @transaction.atomic
    def assign_doctor_to_appointment(appointment_id, department=None):
        """
        Assign doctor cho appointment đã tạo và update status thành confirmed
        """
        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id)
        except Appointment.DoesNotExist:
            raise ValueError("Appointment không tồn tại")
        
        if appointment.status != "pending":
            raise ValueError("Chỉ có thể assign doctor cho appointment có status pending")
        
        # Auto assign doctor
        try:
            doctor_result = AppointmentService.auto_assign_doctor(
                department or "General", 
                appointment.time_start, 
                appointment.end_time
            )
            doctor_id = doctor_result["doctor_id"]
            doctor_info = doctor_result["doctor_info"]
        except ValueError as e:
            raise ValueError(f"Không thể assign bác sĩ: {str(e)}")
        
        # Kiểm tra overlap một lần nữa
        overlap = Appointment.objects.filter(
            doctor_id=doctor_id,
            time_start__lt=appointment.end_time,
            end_time__gt=appointment.time_start
        ).exclude(appointment_id=appointment_id)
        
        if overlap.exists():
            raise ValueError("Bác sĩ đã có lịch trong khoảng thời gian này")
        
        # Tính total_cost = doctor cost * 110%
        doctor_cost = doctor_info.get("cost", 0)
        total_cost = int(doctor_cost * 1.1) if doctor_cost else 0
        
        # Update appointment
        appointment.doctor_id = doctor_id
        appointment.status = "confirmed"
        appointment.total_cost = total_cost
        appointment.save()
        
        # Lấy thông tin patient
        patient_info = UserServiceClient.get_patient_info(appointment.patient_id)
        
        # Trả về thông tin đầy đủ
        result = {
            "appointment_id": str(appointment.appointment_id),
            "time_created": appointment.time_created,
            "time_start": appointment.time_start,
            "end_time": appointment.end_time,
            "status": appointment.status,
            "status_display": appointment.get_status_display(),
            "amount_pay": appointment.amount_pay,
            "total_cost": appointment.total_cost,
            "patient_id": appointment.patient_id,
            "patient_info": patient_info,
            "doctor_id": appointment.doctor_id,
            "doctor_info": doctor_info,
            "message": "Doctor assigned successfully. Appointment confirmed."
        }
        
        return result

    @staticmethod
    @transaction.atomic  
    def create_simple_appointment(data):
        """
        Tạo appointment đơn giản (cho auto-assign view cũ)
        """
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
        """
        Lấy thông tin appointment kèm doctor và patient info
        """
        try:
            appointment = Appointment.objects.get(pk=appointment_id)
            doctor_info = UserServiceClient.get_doctor_info(appointment.doctor_id) if appointment.doctor_id else None
            patient_info = UserServiceClient.get_patient_info(appointment.patient_id)
            
            result = {
                "appointment_id": str(appointment.appointment_id),
                "time_created": appointment.time_created,
                "time_start": appointment.time_start,
                "end_time": appointment.end_time,
                "status": appointment.status,
                "status_display": appointment.get_status_display(),
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
        """
        Cập nhật status của appointment với validation
        """
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
        """
        Tự động assign doctor dựa trên department và thời gian
        """
        # Mock data nếu users chưa có
        mock_doctors = [
            {"id": "doctor-1", "name": "Dr. A"},
            {"id": "doctor-2", "name": "Dr. B"},
        ]
        
        # Gọi API user service để lấy danh sách bác sĩ
        doctors = UserServiceClient.get_doctors_by_department(department)
        if not doctors:
            doctors = mock_doctors

        # Tìm bác sĩ không có lịch trùng
        for doctor in doctors:
            has_overlap = Appointment.objects.filter(
                doctor_id=doctor['id'],
                time_start__lt=end_time,
                end_time__gt=time_start
            ).exists()
            
            if not has_overlap:
                # Sử dụng get_doctor_info để lấy thông tin chi tiết
                doctor_info = UserServiceClient.get_doctor_info(doctor['id'])
                
                if doctor_info:
                    return {
                        "doctor_id": doctor['id'],
                        "doctor_info": doctor_info
                    }
                else:
                    # Fallback nếu không lấy được thông tin chi tiết
                    return {
                        "doctor_id": doctor['id'],
                        "doctor_info": doctor  # Dùng thông tin từ list ban đầu
                    }
        
        raise ValueError("Không tìm thấy bác sĩ nào trống lịch")
    
    @staticmethod
    @transaction.atomic
    def reschedule_appointment(original_id, new_time_start, new_end_time):
        """
        Reschedule appointment - tạo appointment mới và đánh dấu cũ là rescheduled
        """
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

    @staticmethod
    def get_appointment_status(appointment_id):
        """
        Lấy status và thông tin cơ bản của appointment
        """
        try:
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            
            result = {
                "appointment_id": str(appointment.appointment_id),
                "status": appointment.status,
                "status_display": appointment.get_status_display(),
                "doctor_assigned": appointment.doctor_id is not None,
                "total_cost": appointment.total_cost,
                "time_start": appointment.time_start,
                "end_time": appointment.end_time,
                "time_created": appointment.time_created
            }
            
            # Nếu đã assign doctor thì lấy thông tin doctor
            if appointment.doctor_id:
                doctor_info = UserServiceClient.get_doctor_info(appointment.doctor_id)
                result["doctor_info"] = doctor_info
            else:
                result["doctor_info"] = None
            
            return result
            
        except Appointment.DoesNotExist:
            return None