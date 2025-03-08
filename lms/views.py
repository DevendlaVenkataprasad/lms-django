import random
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .models import Student, Teacher
from django.contrib.auth.hashers import make_password

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on role
            if Student.objects.filter(user=user).exists():
                return redirect("student_dashboard")  # Redirect to student dashboard
            elif Teacher.objects.filter(user=user).exists():
                return redirect("teacher_dashboard")  # Redirect to teacher dashboard
            else:
                messages.error(request, "Invalid role. Contact admin.")

        else:
            messages.error(request, "Invalid credentials")

    return render(request, "login.html")


# Send OTP for Registration
def send_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Email already registered."})
        
        otp = str(random.randint(100000, 999999))
        request.session["otp"] = otp
        request.session["email"] = email

        try:
            send_mail(
                "Your OTP for Registration",
                f"Your OTP is: {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            return JsonResponse({"status": "success", "message": "OTP sent successfully."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Failed to send OTP. Error: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request."})

# Verify OTP
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")

        if str(entered_otp) == str(stored_otp):
            return JsonResponse({"success": True})  # ✅ Use Boolean `True`
        else:
            return JsonResponse({"success": False})  # ❌ Use `False`

    return JsonResponse({"error": "Invalid request"}, status=400)


# User Registration

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role_type = request.POST.get("role_type")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another one.")
            return redirect("register")

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect("register")

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("register")

        # Create User
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        if role_type == "student":
            Student.objects.create(user=user, username=username, email=email, password=password, role_type="student")
        elif role_type == "teacher":
            Teacher.objects.create(user=user, username=username, email=email, password=password, role_type="teacher")

        # Send Confirmation Email
        subject = "Welcome to Our LMS Platform!"
        message = f"Dear {username},\n\nYour account has been created successfully!\n\nThank you for registering.\n\nBest Regards,\nLMS Team"
        from_email = "jvsramperla2002@gmail.com" # Use settings-based email
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        messages.success(request, "Registration successful! Check your email for confirmation.")
        return redirect("login")

    return render(request, "register.html")

# Logout
def logout_view(request):
    logout(request)
    return redirect("login")

# Forgot Password
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
            return redirect("forgot_password")

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(reverse("reset_password", args=[user.pk, token]))

        send_mail(
            "Password Reset Request",
            f"Click the link below to reset your password:\n{reset_url}\n\nIf you didn't request this, please ignore this email.",
            settings.EMAIL_HOST_USER,
            [email]
        )

        messages.success(request, "A password reset link has been sent to your email.")
        return redirect("login")

    return render(request, "forgot_password.html")

# Reset Password
def reset_password_view(request, user_id, token):
    user = User.objects.get(pk=user_id)
    if not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired token.")
        return redirect("login")

    if request.method == "POST":
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password successfully reset. You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, "reset_password.html", {"user": user})

# Home Page
def home_view(request):
    return render(request, "home.html")
def student_dashboard_view(request):
    return render(request, "student_dashboard.html")

def teacher_dashboard_view(request):
    return render(request, "teacher_dashboard.html")
from django.http import JsonResponse

def chatbot_response(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "").lower()
        response = get_chatbot_reply(user_message)
        return JsonResponse({"response": response})

def get_chatbot_reply(user_message):
    responses = {
        "hello": "Hello! How can I assist you?",
        "hi": "Hi there! What do you need help with?",
        "courses": "You can access your courses from the dashboard.",
        "how to reset password": "Go to the login page and click on 'Forgot Password'.",
        "bye": "Goodbye! Have a great day!"
    }
    return responses.get(user_message, "I'm sorry, I didn't understand that. Can you rephrase?")



from django.core.files.storage import FileSystemStorage
import os

@login_required
def profile_view(request):
    student = Student.objects.get(user=request.user)

    if request.method == "POST":
        student.username = request.POST.get("username")
        student.email = request.POST.get("email")

        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            fs = FileSystemStorage(location='media/profile_pics/')  # Save inside media/profile_pics/
            filename = fs.save(profile_picture.name, profile_picture)
            student.profile_picture = f"profile_pics/{filename}"

        student.save()
        return redirect("profile")  # Refresh profile page

    return render(request, "profile.html", {"student": student})


