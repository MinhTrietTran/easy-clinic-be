from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Appointment, Schedule, Shift
from .serializers import AppointmentSerializer, ScheduleSerializer, ShiftSerializer
from .services import AppointmentService, UserServiceClient  # Thêm UserServiceClient


class AppointmentListCreateView(APIView):
    def get(self, request):
        appointments = Appointment.objects.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Tạo appointment và trả về ngay, xử lý assign doctor ở background
        """
        # Lấy token từ header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return Response({"error": "Missing or invalid Authorization header"}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header.split(' ')[1]
        
        # Thêm token vào data
        data = request.data.copy()
        data["token"] = token
        
        try:
            # Tạo appointment và trả về ngay
            appointment_result = AppointmentService.create_appointment(data)
            
            # Response ngay cho FE
            return Response({
                **appointment_result,
                "processing_note": "Doctor assignment is being processed in the background. You will receive an email confirmation shortly."
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Lỗi không xác định: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentDetailView(APIView):
    def get(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
            
            # Lấy thông tin patient
            patient_info = None
            if appointment.patient_id:
                patient_info = UserServiceClient.get_patient_info(appointment.patient_id)
            
            # Lấy thông tin doctor nếu đã được assign
            doctor_info = None
            if appointment.doctor_id:
                doctor_info = UserServiceClient.get_doctor_info(appointment.doctor_id)
            
            # Serialize appointment data
            serializer = AppointmentSerializer(appointment)
            
            # Thêm thông tin user vào response
            response_data = serializer.data
            response_data.update({
                "patient_info": patient_info,
                "doctor_info": doctor_info
            })
            
            return Response(response_data)
            
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Lỗi khi lấy thông tin appointment: {str(e)}"}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                
                # Thêm user info vào response sau khi update
                patient_info = None
                if appointment.patient_id:
                    patient_info = UserServiceClient.get_patient_info(appointment.patient_id)
                
                doctor_info = None
                if appointment.doctor_id:
                    doctor_info = UserServiceClient.get_doctor_info(appointment.doctor_id)
                
                response_data = serializer.data
                response_data.update({
                    "patient_info": patient_info,
                    "doctor_info": doctor_info
                })
                
                return Response(response_data)
                
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
            appointment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)


class AppointmentDetailWithUserInfo(APIView):
    def get(self, request, pk):
        """
        Lấy chi tiết appointment với thông tin user (alias cho AppointmentDetailView)
        """
        # Sử dụng lại logic từ service
        result = AppointmentService.get_appointment_detail(pk)
        
        if result:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)


class AppointmentAutoAssignView(APIView):
    def post(self, request):
        department = request.data.get("department")
        time_start = request.data.get("time_start")
        end_time = request.data.get("end_time")
        patient_id = request.data.get("patient_id")

        if not all([department, time_start, end_time, patient_id]):
            return Response({"error": "Thiếu dữ liệu cần thiết"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor_id = AppointmentService.auto_assign_doctor(department, time_start, end_time)
            data = {
                "doctor_id": doctor_id,
                "patient_id": patient_id,
                "time_start": time_start,
                "end_time": end_time
            }
            appointment = AppointmentService.create_appointment(data)
            return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AppointmentStatusView(APIView):
    def get(self, request, pk):
        """
        API để FE check status của appointment
        """
        result = AppointmentService.get_appointment_status(pk)
        
        if result:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)


class AppointmentRescheduleView(APIView):
    def post(self, request, pk):
        new_time_start = request.data.get("new_time_start")
        new_end_time = request.data.get("new_end_time")
        if not all([new_time_start, new_end_time]):
            return Response({"error": "Thiếu thời gian mới"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            new_appointment = AppointmentService.reschedule_appointment(pk, new_time_start, new_end_time)
            return Response(AppointmentSerializer(new_appointment).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ScheduleListCreateView(APIView):
    def get(self, request):
        schedules = Schedule.objects.all()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShiftListCreateView(APIView):
    def get(self, request):
        shifts = Shift.objects.all()
        serializer = ShiftSerializer(shifts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShiftSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentsByDoctorView(APIView):
    def get(self, request, doctor_id):
        """
        Lấy danh sách appointments theo doctor_id
        Query parameters:
        - status: filter theo status (optional)
        - date: filter theo ngày cụ thể (YYYY-MM-DD) (optional)
        """
        status_filter = request.query_params.get('status')
        date_filter = request.query_params.get('date')
        
        try:
            if date_filter:
                # Lấy appointments trong ngày cụ thể
                appointments = AppointmentService.get_appointments_by_doctor_and_date(
                    doctor_id, date_filter, status_filter
                )
            else:
                # Lấy tất cả appointments của doctor
                appointments = AppointmentService.get_appointments_by_doctor(
                    doctor_id, status_filter
                )
            
            return Response({
                "doctor_id": doctor_id,
                "total_appointments": len(appointments),
                "filters": {
                    "status": status_filter,
                    "date": date_filter
                },
                "appointments": appointments
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Lỗi khi lấy appointments: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DoctorScheduleView(APIView):
    def get(self, request, doctor_id):
        """
        Lấy lịch làm việc của doctor theo tuần/tháng
        Query parameters:
        - start_date: ngày bắt đầu (YYYY-MM-DD)
        - end_date: ngày kết thúc (YYYY-MM-DD)
        - status: filter theo status
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status')
        
        try:
            from datetime import datetime, timedelta
            
            # Default: lấy 7 ngày tới
            if not start_date:
                start_date = datetime.now().date()
            else:
                start_date = datetime.fromisoformat(start_date).date()
            
            if not end_date:
                end_date = start_date + timedelta(days=7)
            else:
                end_date = datetime.fromisoformat(end_date).date()
            
            # Query appointments trong khoảng thời gian
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            appointments = Appointment.objects.filter(
                doctor_id=doctor_id,
                time_start__gte=start_datetime,
                time_start__lte=end_datetime
            )
            
            if status_filter:
                appointments = appointments.filter(status=status_filter)
            
            appointments = appointments.order_by('time_start')
            
            # Group theo ngày
            schedule = {}
            for appointment in appointments:
                date_key = appointment.time_start.date().isoformat()
                if date_key not in schedule:
                    schedule[date_key] = []
                
                patient_info = UserServiceClient.get_patient_info(appointment.patient_id)
                
                schedule[date_key].append({
                    "appointment_id": str(appointment.appointment_id),
                    "time_start": appointment.time_start,
                    "end_time": appointment.end_time,
                    "status": appointment.status,
                    "status_display": appointment.get_status_display(),
                    "patient_id": appointment.patient_id,
                    "patient_info": patient_info,
                    "total_cost": appointment.total_cost
                })
            
            return Response({
                "doctor_id": doctor_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_appointments": appointments.count(),
                "schedule": schedule
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Lỗi khi lấy lịch doctor: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AppointmentsByPatientView(APIView):
    def get(self, request, patient_id):
        """
        Lấy danh sách appointments theo patient_id
        Query parameters:
        - status: filter theo status (optional)
        - limit: số lượng appointments (default: 10)
        """
        status_filter = request.query_params.get('status')
        limit = int(request.query_params.get('limit', 10))
        
        try:
            appointments = AppointmentService.get_appointments_by_patient(
                patient_id, status_filter, limit
            )
            
            return Response({
                "patient_id": patient_id,
                "total_appointments": len(appointments),
                "limit": limit,
                "appointments": appointments
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "error": f"Lỗi khi lấy appointments: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AppointmentStatisticsView(APIView):
    def get(self, request):
        """
        Lấy thống kê tổng quan appointments
        """
        try:
            stats = AppointmentService.get_appointment_statistics()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"Lỗi khi lấy thống kê: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DoctorStatisticsView(APIView):
    def get(self, request, doctor_id):
        """
        Lấy thống kê của doctor cụ thể
        """
        try:
            stats = AppointmentService.get_doctor_statistics(doctor_id)
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": f"Lỗi khi lấy thống kê doctor: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
