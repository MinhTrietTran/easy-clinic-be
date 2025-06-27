from django.contrib.auth import authenticate
from ..models.user import CustomUser
from ..models.patient import Patient


def register_user(data):
    user = CustomUser.objects.create_user(
            email = data['email'],
            password=data['password'],
            role=data.get('role','patient'), # Default: patient
            phone=data.get('phone', None),
        )
    if user.role == 'patient':
        gender=data.get('gender','').lower()
        gender_value = True if gender == 'female' else False
        Patient.objects.create(
            user=user,
            first_name = data.get('first_name',''),
            last_name=data.get('last_name', ''),
            gender=gender_value,
            DOB=data.get('dob',''),
            address=data.get('address',''),
            allergies=data.get('allergies',''),
            chronic_diseases=data.get('choronic_diseases'),
        )
    return user


def login(data):
    email = data.get('email')
    password = data.get('password')
    # Authenticate
    user = authenticate(email=email, password=password)
    return user