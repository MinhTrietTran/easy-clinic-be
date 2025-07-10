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
)

urlpatterns = [
    # Appointment APIs
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),  # GET, POST
    path('appointments/auto-assign/', AppointmentAutoAssignView.as_view(), name='appointment-auto-assign'),  # POST
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),  # GET, PUT, DELETE
    path('appointments/<int:pk>/with-info/', AppointmentDetailWithUserInfo.as_view(), name='appointment-detail-info'),  # GET
    path('appointments/<uuid:pk>/status/', AppointmentStatusView.as_view(), name='appointment-status'),  # GET
    path('appointments/<int:pk>/reschedule/', AppointmentRescheduleView.as_view(), name='appointment-reschedule'),  # PATCH/PUT

    # Schedule & Shift APIs
    path('schedules/', ScheduleListCreateView.as_view(), name='schedule-list-create'),  # GET, POST
    path('shifts/', ShiftListCreateView.as_view(), name='shift-list-create'),  # GET, POST
]
