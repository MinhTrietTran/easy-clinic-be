from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'check-appointments-every-day': {
        'task': 'notifications.tasks.fetch_and_notify_appointments',
        'schedule': crontab(hour=0, minute=0),  # Runs daily at midnight UTC
    },
    'check-prescriptions-every-day': {
        'task': 'notifications.tasks.fetch_and_notify_prescriptions',
        'schedule': crontab(hour=0, minute=0),  # Runs daily at midnight UTC
    },
}