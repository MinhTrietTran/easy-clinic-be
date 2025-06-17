from django.contrib import admin
from .models import CustomUser, Doctor, Patient

admin.site.register(CustomUser)
admin.site.register(Doctor)
admin.site.register(Patient)
