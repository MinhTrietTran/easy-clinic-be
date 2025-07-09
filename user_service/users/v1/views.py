from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .tokens import CustomRefreshToken
from .services import *
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# ...existing code...

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_me(request.user)
        return Response(data)

    def put(self, request):
        try:
            updated_data = update_user_profile(request.user, request.data)
            return Response(updated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        data = request.data
        try:
            result = register_user(request.data)
            return Response({"message":"User registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        user = login(request.data)
        if user:
            # Create jwt
            refresh = CustomRefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                # "role": user.role # Return user role
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class DoctorListByDepartmentView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        department = request.GET.get('department')
        if not department:
            return Response({"error": "Missing department"}, status=status.HTTP_400_BAD_REQUEST)
        data = get_doctors_by_department(department)
        return Response(data)
    
class DoctorDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        data = get_doctor_info(doctor_id=doctor_id)
        if not data:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)

class PatientDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        data = get_patient_info(patient_id=patient_id)
        if not data:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)