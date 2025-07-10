from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Appointment, Schedule, Shift
from .serializers import AppointmentSerializer, ScheduleSerializer, ShiftSerializer
from .services import AppointmentService


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
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
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
        result = AppointmentService.get_appointment_with_user_info(pk)
        if result:
            return Response(result)
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
