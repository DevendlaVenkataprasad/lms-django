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

from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from .models import Student, Teacher  # Import both models

@login_required
def update_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value")

        # Try to get student or teacher profile
        student = Student.objects.filter(user=request.user).first()
        teacher = Teacher.objects.filter(user=request.user).first()

        profile = student if student else teacher
        
        if not profile:
            return JsonResponse({"status": "error", "message": "Profile not found"}, status=404)

        # Update the profile field
        if hasattr(profile, field):
            setattr(profile, field, value)
            profile.save()
            return JsonResponse({"status": "success", "message": f"{field} updated successfully!"})
        
        return JsonResponse({"status": "error", "message": "Invalid field"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Student, Teacher

@login_required
def upload_profile_picture(request):
    if request.method == "POST" and request.FILES.get("profile_picture"):
        image = request.FILES["profile_picture"]
        image_path = f"profile_pictures/{request.user.id}_{image.name}"
        
        # Save the image using Django's default storage
        saved_path = default_storage.save(image_path, ContentFile(image.read()))
        
        # Check if the user is a student or a teacher and update accordingly
        student = Student.objects.filter(user=request.user).first()
        teacher = Teacher.objects.filter(user=request.user).first()
        
        if student:
            student.profile_picture = saved_path
            student.save()
            return JsonResponse({"status": "success", "image_url": student.profile_picture.url})
        
        if teacher:
            teacher.profile_picture = saved_path
            teacher.save()
            return JsonResponse({"status": "success", "image_url": teacher.profile_picture.url})
        
        return JsonResponse({"status": "error", "message": "User not associated with Student or Teacher model"}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Teacher  # Import both models

@login_required
@csrf_exempt  # Allows AJAX requests (Use CSRF token in production)
def edit_profile(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data
            field = data.get("field")  # Get the field name
            value = data.get("value")  # Get the new value

            # Check if the user is a student or a teacher
            student = Student.objects.filter(user=request.user).first()
            teacher = Teacher.objects.filter(user=request.user).first()

            profile = student if student else teacher  # Determine profile type

            if not profile:
                return JsonResponse({"status": "error", "message": "Profile not found"}, status=404)

            # Check if the field exists in the model
            if hasattr(profile, field):
                setattr(profile, field, value)  # Update field
                profile.save()  # Save changes

                return JsonResponse({"status": "success", "message": f"{field} updated successfully!"})

            return JsonResponse({"status": "error", "message": "Invalid field"}, status=400)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)



from django.shortcuts import render, redirect, get_object_or_404
from .models import Education
from .forms import EducationForm
from django.contrib.auth.decorators import login_required

@login_required
def edit_education(request):
    if request.method == "POST":
        education_id = request.POST.get("education_id")

        # Fetch the education record for the logged-in user
        if hasattr(request.user, 'student'):  # If the user is a student
            education = get_object_or_404(Education, id=education_id, student=request.user.student)
        elif hasattr(request.user, 'teacher'):  # If the user is a teacher
            education = get_object_or_404(Education, id=education_id, teacher=request.user.teacher)
        else:
            return redirect("profile")  # If neither, redirect back

        form = EducationForm(request.POST, request.FILES, instance=education)
        if form.is_valid():
            form.save()
            return redirect("profile")  # Redirect back to profile page after saving
        else:
            print(form.errors)  # Debugging: Print form errors in the terminal

    return redirect("profile")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Student, Teacher, Education, Internship, Skill

@login_required
def profile_view(request):
    # Determine if user is a student or teacher
    student = getattr(request.user, 'student', None)
    teacher = getattr(request.user, 'teacher', None)

    # Redirect if neither student nor teacher
    if not (student or teacher):
        return redirect('dashboard')

    # Assign user role
    user_profile = student if student else teacher
    is_student = student is not None
    is_teacher = teacher is not None

    # Fetch education, internships, and skills for the logged-in user
    education_list = Education.objects.filter(student=student) if is_student else Education.objects.filter(teacher=teacher)
    internship_list = Internship.objects.filter(student=student) if is_student else Internship.objects.filter(teacher=teacher)
    skills_list = Skill.objects.filter(student=student) if is_student else Skill.objects.filter(teacher=teacher)

    if request.method == "POST":
        # Add Education
        if 'institution_name' in request.POST:
            Education.objects.create(
                student=student if is_student else None,
                teacher=teacher if is_teacher else None,
                institution_name=request.POST.get('institution_name'),
                degree=request.POST.get('degree'),
                field_of_study=request.POST.get('field_of_study'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                grade=request.POST.get('grade'),
                institution_logo=request.FILES.get('institution_logo')
            )
            return redirect('profile')

        # Add Internship
        if 'company_name' in request.POST:
            Internship.objects.create(
                student=student if is_student else None,
                teacher=teacher if is_teacher else None,
                company_name=request.POST.get('company_name'),
                role=request.POST.get('role'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date')
            )
            return redirect('profile')

        # Add Skill
        if 'skill_name' in request.POST:
            Skill.objects.create(
                student=student if is_student else None,
                teacher=teacher if is_teacher else None,
                name=request.POST.get('skill_name')
            )
            return redirect('profile')  # Ensure the page refreshes

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'is_student': is_student,
        'is_teacher': is_teacher,
        'education_list': education_list,
        'internship_list': internship_list,
        'skills_list': skills_list,
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Education

@login_required
def delete_education(request, education_id):
    education = get_object_or_404(Education, id=education_id)

    # Ensure only the owner (student/teacher) can delete the record
    student_user = getattr(education.student, 'user', None)
    teacher_user = getattr(education.teacher, 'user', None)

    if request.user == student_user or request.user == teacher_user:
        education.delete()
        return redirect('profile')  # Redirect back to profile after deletion
    else:
        return HttpResponseForbidden("You are not authorized to delete this record.")  # Return 403 if unauthorized
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Internship

def delete_internship(request, internship_id):
    if request.method == "POST":
        internship = get_object_or_404(Internship, id=internship_id)

        # Check ownership for students and teachers
        if (internship.student and internship.student.user == request.user) or \
           (internship.teacher and internship.teacher.user == request.user):
            internship.delete()
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Internship

def save_internship(request):
    if request.method == "POST":
        internship_id = request.POST.get("internship_id")  # Get internship ID from the form

        # If an ID is provided, update the existing record
        if internship_id:
            internship = get_object_or_404(Internship, id=internship_id)

            # Check if the logged-in user owns this internship
            if (internship.student and internship.student.user == request.user) or \
               (internship.teacher and internship.teacher.user == request.user):
                internship.company_name = request.POST["company_name"]
                internship.role = request.POST["role"]
                internship.start_date = request.POST["start_date"]
                internship.end_date = request.POST["end_date"]
                internship.save()
                return JsonResponse({"success": True, "message": "Internship updated successfully!"})
            else:
                return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
        
        # If no ID is provided, create a new internship (New Entry)
        else:
            user_type = request.POST.get("user_type")
            if user_type == "student":
                internship = Internship.objects.create(
                    student=request.user.student,  # Associate with student
                    company_name=request.POST["company_name"],
                    role=request.POST["role"],
                    start_date=request.POST["start_date"],
                    end_date=request.POST["end_date"],
                )
            elif user_type == "teacher":
                internship = Internship.objects.create(
                    teacher=request.user.teacher,  # Associate with teacher
                    company_name=request.POST["company_name"],
                    role=request.POST["role"],
                    start_date=request.POST["start_date"],
                    end_date=request.POST["end_date"],
                )

            return JsonResponse({"success": True, "message": "Internship added successfully!"})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
