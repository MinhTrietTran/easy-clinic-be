from rest_framework import serializers
from ..models import Appointment, Schedule, Shift


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['schedule_id', 'time_from', 'time_to', 'is_active']


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['shift_id', 'time_start', 'time_end', 'is_archived']


class AppointmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'appointment_id',
            'time_created',
            'time_start',
            'end_time',
            'status',
            'status_display',
            'amount_pay',
            'total_cost',
            'patient_id',
            'doctor_id',
            'schedule',
            'shift'
        ]

    def validate(self, data):
        """
        Kiểm tra bác sĩ đã có lịch trong khoảng thời gian trùng hay chưa.
        """
        doctor_id = data.get('doctor_id')
        time_start = data.get('time_start')
        end_time = data.get('end_time')

        if doctor_id and time_start and end_time:
            # Nếu đang update thì bỏ qua bản ghi hiện tại
            instance = self.instance
            overlaps = Appointment.objects.filter(
                doctor_id=doctor_id,
                time_start__lt=end_time,
                end_time__gt=time_start
            )
            if instance:
                overlaps = overlaps.exclude(pk=instance.pk)

            if overlaps.exists():
                raise serializers.ValidationError("❌ Lịch của bác sĩ đã bị trùng với một cuộc hẹn khác.")

        return data
