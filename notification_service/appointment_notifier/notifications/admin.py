from django.contrib import admin
from .models import Appointment, Prescription

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'patient_email', 'appointment_date', 'appointment_time', 'notified')
    list_filter = ('notified', 'appointment_date')
    search_fields = ('appointment_id', 'patient_email')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('prescription_id', 'patient_email', 'ready_date', 'medication', 'notified')
    list_filter = ('notified', 'ready_date')
    search_fields = ('prescription_id', 'patient_email')