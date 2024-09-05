from .views import RegistrationView
from django.urls import path, include



urlpatterns = [
    path('register', RegistrationView.as_view(), name="register")
]