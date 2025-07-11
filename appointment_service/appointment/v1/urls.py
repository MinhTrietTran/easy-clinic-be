from django.urls import path
from .views import (
    AppointmentListCreateView,
    AppointmentDetailView,
    AppointmentDetailWithUserInfo,
    AppointmentAutoAssignView,
    AppointmentRescheduleView,
    ScheduleListCreateView,
    ShiftListCreateView,
    AppointmentStatusView,
    AppointmentsByDoctorView,      # Thêm
    DoctorScheduleView,            # Thêm
    AppointmentsByPatientView,     # Thêm
    AppointmentStatisticsView,     # Thêm
    DoctorStatisticsView,          # Thêm
)

urlpatterns = [
    # Appointment APIs
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),  # GET, POST
    path('appointments/auto-assign/', AppointmentAutoAssignView.as_view(), name='appointment-auto-assign'),  # POST
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),  # GET, PUT, DELETE
    path('appointments/<int:pk>/with-info/', AppointmentDetailWithUserInfo.as_view(), name='appointment-detail-info'),  # GET
    path('appointments/<uuid:pk>/status/', AppointmentStatusView.as_view(), name='appointment-status'),  # GET
    path('appointments/<int:pk>/reschedule/', AppointmentRescheduleView.as_view(), name='appointment-reschedule'),  # PATCH/PUT
    
    # Doctor Appointments APIs
    path('appointments/doctor/<str:doctor_id>/', AppointmentsByDoctorView.as_view(), name='doctor-appointments'),
    path('doctors/<str:doctor_id>/schedule/', DoctorScheduleView.as_view(), name='doctor-schedule'),
    path('doctors/<str:doctor_id>/statistics/', DoctorStatisticsView.as_view(), name='doctor-statistics'),
    
    # Patient Appointments APIs
    path('patients/<str:patient_id>/appointments/', AppointmentsByPatientView.as_view(), name='patient-appointments'),
    
    # Statistics APIs
    path('statistics/dashboard/', AppointmentStatisticsView.as_view(), name='appointment-statistics'),
    
    # Schedule & Shift APIs
    path('schedules/', ScheduleListCreateView.as_view(), name='schedule-list-create'),  # GET, POST
    path('shifts/', ShiftListCreateView.as_view(), name='shift-list-create'),  # GET, POST
]
