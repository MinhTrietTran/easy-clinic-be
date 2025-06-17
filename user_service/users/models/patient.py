from django.db import models
from .user import CustomUser  # hoặc từ users.models.user import CustomUser

class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.BooleanField()  # True: Female, False: Male
    DOB = models.DateField()
    address = models.CharField(max_length=255)
    allergies = models.TextField(blank=True)
    chronic_diseases = models.TextField(blank=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

