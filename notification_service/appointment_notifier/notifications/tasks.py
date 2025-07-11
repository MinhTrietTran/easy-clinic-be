from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import date
from .models import Appointment, Prescription

@shared_task
def process_appointment_data(data):
    
    appointment = Appointment.objects.create(
        appointment_id=data['id'],
        patient_email=data['patient_email'],
        appointment_date=data['date'],
        appointment_time=data['time'],
        notified=False
    )
    
    send_mail(
        subject='Appointment Confirmation',
        message=f'Your appointment scheduled for {data["date"]} at {data["time"]} has been confirmed.',
        from_email= settings.EMAIL_HOST_USER,  # Replace with your email
        recipient_list=[appointment['patient_email']],
        fail_silently=False,
    )

    today = timezone.now().date()  # Get current date in ICT timezone
    if appointment.appointment_date == today:
        send_mail(
            subject='Appointment Reminder',
            message=f'Reminder: You have an appointment today at {appointment.time}.',
            from_email=settings.EMAIL_HOST_USER,  # Replace with your configured sender email
            recipient_list=[appointment.patient_email],
            fail_silently=False,
        )
        appointment.notified = True
        appointment.save()

@shared_task
def check_and_send_reminders():
    """
    Periodic task to check for appointments due today and send reminders.
    Runs daily at 00:00 .
    """
    today = timezone.now().date()
    due_appointments = Appointment.objects.filter(appointment_date=today, notified=False)
    for appointment in due_appointments:
        send_mail(
            subject='Appointment Reminder',
            message=f'Reminder: You have an appointment today at {appointment.time}.',
            from_email=settings.EMAIL_HOST_USER,  # Replace with your configured sender email
            recipient_list=[appointment.patient_email],
            fail_silently=False,
        )
        appointment.notified = True
        appointment.save()

@shared_task
def process_prescription_data(data):
    prescription = Prescription.objects.create(
        id=data['id'],
        patient_email=data['patient_email'],
        medication=data['medication'],
        notified=False
    )
    
    send_mail(
        subject='Prescription ready',
        message=f'Your prescription is ready for pick up, please come to the clinic and pick it up.',
        from_email= settings.EMAIL_HOST_USER,  
        recipient_list=[data['patient_email']],
        fail_silently=False,
    )
    prescription.notified = True
    prescription.save()



