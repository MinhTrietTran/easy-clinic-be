from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import date
from .models import Appointment, Prescription
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_appointment_data(data):
    try:
        # Check if appointment already exists to avoid duplicate
        existing_appointment = Appointment.objects.filter(
            appointment_id=data['id']
        ).first()
        
        if existing_appointment:
            logger.info(f"Appointment {data['id']} already exists, using existing")
            appointment = existing_appointment
        else:
            # Create new appointment - FIX: Đổi data['email'] thành data['patient_email']
            appointment = Appointment.objects.create(
                appointment_id=data['id'],
                patient_email=data['patient_email'],  # ✅ FIX: Đổi từ data['email']
                appointment_date=data['date'],
                appointment_time=data['time'],
                notified=False
            )
            logger.info(f"Created new appointment {data['id']}")
        
        # Send confirmation email - FIX: Đổi appointment['patient_email'] thành appointment.patient_email
        send_mail(
            subject='Appointment Confirmation',
            message=f'Your appointment scheduled for {data["date"]} at {data["time"]} has been confirmed.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[appointment.patient_email],  # ✅ FIX: Đổi từ appointment['patient_email']
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent to {appointment.patient_email}")

        # Check if appointment is today and send reminder
        today = timezone.now().date()
        if str(appointment.appointment_date) == str(today):
            send_mail(
                subject='Appointment Reminder',
                message=f'Reminder: You have an appointment today at {appointment.appointment_time}.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[appointment.patient_email],
                fail_silently=False,
            )
            appointment.notified = True
            appointment.save()
            logger.info(f"Reminder email sent to {appointment.patient_email}")
            
        return f"Email sent successfully to {appointment.patient_email}"
        
    except Exception as e:
        logger.error(f"Error processing appointment data: {str(e)}")
        raise e

@shared_task
def check_and_send_reminders():
    """
    Periodic task to check for appointments due today and send reminders.
    Runs daily at 00:00.
    """
    try:
        today = timezone.now().date()
        due_appointments = Appointment.objects.filter(appointment_date=today, notified=False)
        
        for appointment in due_appointments:
            send_mail(
                subject='Appointment Reminder',
                message=f'Reminder: You have an appointment today at {appointment.appointment_time}.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[appointment.patient_email],
                fail_silently=False,
            )
            appointment.notified = True
            appointment.save()
            logger.info(f"Reminder sent to {appointment.patient_email}")
            
    except Exception as e:
        logger.error(f"Error in check_and_send_reminders: {str(e)}")
        raise e

@shared_task
def process_prescription_data(data):
    try:
        prescription = Prescription.objects.create(
            id=data['id'],
            patient_email=data['patient_email'],
            medication=data['medication'],
            notified=False
        )
        
        send_mail(
            subject='Prescription Ready',
            message=f'Your prescription is ready for pick up, please come to the clinic and pick it up.',
            from_email=settings.EMAIL_HOST_USER,  
            recipient_list=[data['patient_email']],
            fail_silently=False,
        )
        prescription.notified = True
        prescription.save()
        logger.info(f"Prescription notification sent to {data['patient_email']}")
        
    except Exception as e:
        logger.error(f"Error processing prescription data: {str(e)}")
        raise e



