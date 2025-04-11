from django.shortcuts import render,redirect
from django.http import HttpRequest
from django.contrib.auth.models import User 
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
verification_codes= {}

def generate_verification_code():
    return str(random.randint(100000, 999999))


def send_verification_code_email(user_email,code):
    subject = 'Your Email Verification Code'
    message = f"Your verification code is: {code}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])

# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        try:
            new_user = User.objects.create_user(
                username=username,
                email=email,
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                password=request.POST['password']
            )
            new_user.is_active = False
            new_user.save()

            # Send verification code
            code = generate_verification_code()
            verification_codes[email] = code
            send_verification_code_email(email, code)


        except IntegrityError:
            messages.error(request, "Failed to register user due to a database error.", "alert-danger")
        except Exception as e:
            print(e)
            messages.error(request, "Unexpected error during signup.", "alert-danger")
        return render(request, "accounts/enter_code.html", {"email": email})


    return render(request, "accounts/signup.html")
def verify_view(request):
   
    if request.method == 'POST':
        code = request.POST.get('code')
        email = request.POST.get('email')
        expected_code = verification_codes.get(email)
        
        if expected_code and code == expected_code:
            user = User.objects.filter(email=email).order_by('-id').first()
            if user:
                user.is_active = True
                user.save()
                messages.success(request, "User registered successfully", "alert-success")
                return redirect('accounts:login_view')
            else:
                messages.error(request, "User not found.", "alert-danger")
        else:
            messages.error(request, "Invalid verification code.", "alert-danger")

    return render(request, "accounts/enter_code.html", {"email": email})
def login_view(request:HttpRequest):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'],password=request.POST['password'])
        if user :
            login(request,user)
            messages.success(request,f"welome {user.username}, you logged in successfuly","alert-success")
            return redirect('home')
        else:
            messages.success(request,"no such user , try again !","alert-danger")
    return render(request,'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request,"logged out successfuly ", "alert-warning")
    return redirect('accounts:login_view')



'''
> front-end 

'''