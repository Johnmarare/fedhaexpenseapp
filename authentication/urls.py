from .views import RegistrationView, UsernameValidationView, EmailValidationView, CompletePasswordResetView,  VerificationView, LoginView, LogoutView, RequestPwdResetEmail
from django.urls import path
from django.views.decorators.csrf import csrf_exempt



urlpatterns = [
    path('register', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), 
                                        name="validate-username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate-email"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate"),
    path('set-newpassword/<uidb64>/<token>', CompletePasswordResetView.as_view(), name="reset-user-password"),
    path('request-renew-link', RequestPwdResetEmail.as_view(), name="request-renew-link")
]