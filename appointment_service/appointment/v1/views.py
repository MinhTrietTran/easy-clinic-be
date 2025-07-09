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
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                appointment = AppointmentService.create_appointment(serializer.validated_data)
                return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class AppointmentStatusUpdateView(APIView):
    def post(self, request, pk):
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Thiếu trạng thái mới"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            appointment = AppointmentService.update_appointment_status(pk, new_status)
            return Response(AppointmentSerializer(appointment).data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
