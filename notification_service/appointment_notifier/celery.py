import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_notifier.settings')

app = Celery('appointment_notifier')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['appointment_notifier.notifications'])