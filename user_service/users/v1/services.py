from django.contrib.auth import authenticate
from ..models.user import CustomUser
from ..models.patient import Patient
from ..models.doctor import Doctor


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

def get_me(user):
    data = {
        "user_id": str(user.user_id),
        "email": user.email,
        "phone": user.role,
        "created_at": user.created_at,
    }
    if user.role == "patient":
        try:
            patient = Patient.objects.get(user=user)
            data.update({
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "gender": "female" if patient.gender else "male",
                "dob": patient.DOB,
                "address": patient.address,
                "allergies": patient.allergies,
                "chronic_diseases": patient.chronic_diseases,
            })
        except Patient.DoesNotExist:
            data["detail"] = "Patient profile not found"
    elif user.role == "doctor":
        try:
            doctor = Doctor.objects.get(user=user)
            data.update({
                "first_name": doctor.first_name,
                "last_name": doctor.last_name,
                "department": doctor.department,
                "cost": doctor.cost,
                "is_active": doctor.is_active,
            })
        except Doctor.DoesNotExist:
            data['detail'] = "Doctor profile not found"
    return data

def update_user_profile(user, data):
    # Update CustomUser fields if provided
    user.phone = data.get('phone', user.phone)
    user.save()

    if user.role == "patient":
        try:
            patient = Patient.objects.get(user=user)
            patient.first_name = data.get('first_name', patient.first_name)
            patient.last_name = data.get('last_name', patient.last_name)
            patient.gender = True if data.get('gender', '').lower() == 'female' else False
            patient.DOB = data.get('dob', patient.DOB)
            patient.address = data.get('address', patient.address)
            patient.allergies = data.get('allergies', patient.allergies)
            patient.chronic_diseases = data.get('chronic_diseases', patient.chronic_diseases)
            patient.save()
        except Patient.DoesNotExist:
            raise Exception("Patient profile not found")
    elif user.role == "doctor":
        try:
            doctor = Doctor.objects.get(user=user)
            doctor.first_name = data.get('first_name', doctor.first_name)
            doctor.last_name = data.get('last_name', doctor.last_name)
            doctor.department = data.get('department', doctor.department)
            doctor.cost = data.get('cost', doctor.cost)
            doctor.is_active = data.get('is_active', doctor.is_active)
            doctor.save()
        except Doctor.DoesNotExist:
            raise Exception("Doctor profile not found")

    return get_me(user) # Return updated data using existing get_me function
    

