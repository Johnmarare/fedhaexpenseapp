from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage

from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from .utils import account_activation_token
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading
# Create your views here.


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    
    def run(self):
        self.email.send(fail_silently=False)


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'A user with this name already exists, use a diffrent name '}, status=409)
        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Email already exists, use a diffrent email '}, status=409)
        return JsonResponse({'email_valid': True})



class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        # Get a user
        # Validate user
        # create user account


        # Get form data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        # Validate user input
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "password too short")
                    return render(request, 'authentication/register.html', context)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                # Prepare account activation email
                current_site = get_current_site(request)
                email_content = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }
                
                link = reverse('activate', kwargs={
                    'uidb64': email_content['uid'], 'token': email_content['token']})
        

                activate_url = 'http://' + current_site.domain + link

                email_subject = 'Activate your account'
                email_message = f"Hi {user.username}, \nPlease click the link below to activate your account \n{activate_url}"
                
                email = EmailMessage(
                    email_subject,
                    email_message,
                    'noreply@fedha.com',
                    [email],
                )

                EmailThread(email).start()

                # Inform user to check email
                messages.success(request, 'Your account has been created! Please check your email to activate your account.')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')
    

class VerificationView(View):
    def get(self, request, uidb64, token):

        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?messages='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')
        
        except Exception as e:
            pass

        return redirect('login')
    
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username+' you are now logged in')
                    return redirect('expenses')
                messages.error(
                    request, 'Account is not active,please check your email')
                return render(request, 'authentication/login.html')
            messages.error(
                request, 'Invalid credentials,try again')
            return render(request, 'authentication/login.html')

        messages.error(
            request, 'Please fill all fields')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')


class RequestPwdResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST['email']
        
        if not validate_email(email):
            messages.error(request, 'Please input a valid email')
            return render(request, 'authentication/reset-password.html')
        
        current_site = get_current_site(request)
        user = User.objects.filter(email=email)

        if user.exists():
                    email_content = {
                    'user': user[0],
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                    'token': PasswordResetTokenGenerator().make_token(user[0]),
                }
                
                    link = reverse('reset-user-password', kwargs={
                    'uidb64': email_content['uid'], 'token': email_content['token']})
        

                    reset_url = 'http://' + current_site.domain + link

                    email_subject = 'Password Reset Instructions'
                    email_message = f"Hi there, \nPlease click the link below to reset your password  \n{reset_url}"
                
                    email = EmailMessage(
                                email_subject,
                                email_message,
                                'noreply@fedha.com',
                                [email],
                            )

                    EmailThread(email).start()

        messages.success(request, 'we have sent an email link to reset your password')


        return render(request, 'authentication/login.html')


class CompletePasswordResetView(View):
    def get(self, request, uidb64, token):
        context = {'uidb64': uidb64, 'token': token}

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            # Check if the token is valid
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'This password reset link is invalid or has already been used. Please request a new one.')
                return redirect('request-renew-link')

        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            messages.error(request, 'Invalid or expired link, please request a new one.')
            return redirect('request-renew-link')

        return render(request, 'authentication/set-newpassword.html', context)

    def post(self, request, uidb64, token):
        context = {'uidb64': uidb64, 'token': token, 'has_error': False}

        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validate password length and match
        if len(password) < 6:
            messages.error(request, 'Password should be at least 6 characters long.')
            context['has_error'] = True
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'authentication/set-newpassword.html', context)

        try:
            # Decode user ID and retrieve the user
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            # Check if the token is still valid (hasn't expired or been used already)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'This password reset link is invalid or has already been used. Please request a new one.')
                return redirect('request-renew-link')

            # Set the new password
            user.set_password(password)
            user.save()

            messages.success(request, 'Password reset successful, you can now log in.')
            return redirect('login')

        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            messages.error(request, 'Something went wrong, please try again.')
            return redirect('request-renew-link')

        return render(request, 'authentication/set-newpassword.html', context)