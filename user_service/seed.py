import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings')
django.setup()

from users.models.user import CustomUser
from users.models.doctor import Doctor
from users.models.patient import Patient

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def seed_users():
    # Tạo admin
    for i in range(1, 4):
        email = f'admin{i}@example.com'
        if not CustomUser.objects.filter(email=email).exists():
            CustomUser.objects.create_superuser(
                email=email,
                password='admin123'
            )
            print("Created admin:", email)

    # Tạo doctor
    departments = [
        'Cardiology', 'Neurology', 'Pediatrics', 'Dermatology', 'Oncology',
        'Orthopedics', 'Gastroenterology', 'Endocrinology', 'Ophthalmology', 'Psychiatry'
    ]
    for i in range(1, 61):
        email = f'doctor{i}@example.com'
        if not CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.create_user(
                email=email,
                password='doctor123',
                role='doctor'
            )
            Doctor.objects.create(
                user=user,
                first_name=f'Doctor{i}',
                last_name='Nguyen',
                department=random.choice(departments),
                cost=random.randint(300000, 800000),
                is_active=True
            )
            print("Created doctor:", email)

    # Tạo patient
    for i in range(1, 11):
        email = f'patient{i}@example.com'
        if not CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.create_user(
                email=email,
                password='patient123',
                role='patient'
            )
            Patient.objects.create(
                user=user,
                first_name=f'Patient{i}',
                last_name='Le',
                gender=random.choice([True, False]),
                DOB=random_date(date(1980, 1, 1), date(2010, 12, 31)),
                address=f'{i} Main St',
                allergies=random.choice(['None', 'Penicillin', 'Seafood']),
                chronic_diseases=random.choice(['None', 'Diabetes', 'Hypertension'])
            )
            print("Created patient:", email)

if __name__ == "__main__":
    seed_users()