from django.urls import path
from .views import RegisterView, LoginView, MeView
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
]