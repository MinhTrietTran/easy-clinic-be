from django.urls import path
from .views import (
    AppointmentListCreateView,
    AppointmentDetailView,
    AppointmentDetailWithUserInfo,
    AppointmentAutoAssignView,
    AppointmentStatusUpdateView,
    AppointmentRescheduleView,
    ScheduleListCreateView,
    ShiftListCreateView,
)

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view()),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view()),
    path('appointments/<int:pk>/with-info/', AppointmentDetailWithUserInfo.as_view()),
    path('appointments/auto-assign/', AppointmentAutoAssignView.as_view()),
    path('appointments/<int:pk>/status/', AppointmentStatusUpdateView.as_view()),
    path('appointments/<int:pk>/reschedule/', AppointmentRescheduleView.as_view()),
    path('schedules/', ScheduleListCreateView.as_view()),
    path('shifts/', ShiftListCreateView.as_view()),
]
