from django.urls import path
from .views import (
    AppointmentListCreateView, AppointmentDetailView,
    ScheduleListCreateView, ShiftListCreateView
)

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view()),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view()),
    path('schedules/', ScheduleListCreateView.as_view()),
    path('shifts/', ShiftListCreateView.as_view()),
]
