from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ..models.user import CustomUser
from ..models.patient import Patient

# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        data = request.data
        try:
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
            return Response({"message":"User registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
