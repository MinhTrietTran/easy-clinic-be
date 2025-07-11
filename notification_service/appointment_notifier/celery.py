from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_notifier.settings')

# Initialize Django to load the app registry
django.setup()

# Now create the Celery app
app = Celery('appointment_notifier')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in the 'notifications' app
app.autodiscover_tasks(['appointment_notifier.notifications'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')