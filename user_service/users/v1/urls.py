from django.urls import path
from .views import (
    RegisterView, LoginView, MeView,
    DoctorListByDepartmentView, DoctorDetailView, PatientDetailView, 
    GetPatientIdView, GetDoctorIdView  # Thêm import
)
from rest_framework_simplejwt.views import ( # type: ignore
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),

    # JWT built-in
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Doctor and Patient details
    path('doctors/', DoctorListByDepartmentView.as_view(), name='doctor-list-by-department'),
    path('doctors/<int:doctor_id>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('patients/<int:patient_id>/', PatientDetailView.as_view(), name='patient-detail'),
    
    # Get IDs from token
    path('patient/me/id/', GetPatientIdView.as_view(), name='get-patient-id'),
    path('doctor/me/id/', GetDoctorIdView.as_view(), name='get-doctor-id'),  # Thêm URL mới
]