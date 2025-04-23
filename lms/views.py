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

import os
from django.contrib import messages
from .models import Video,Document,Quiz, Question, Option
from .forms import VideoFormSet,DocumentForm



from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Enrollment, CourseContent
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Course
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
from .models import Student, Teacher, Education, Internship, Skill,StudentAnswer

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


def add_content(request):
    return render(request,'add_content.html')
def view_all(request):
    return render(request,'view_all.html')

""" Documents"""


def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_document')  # Redirect to the list view after successful upload
    else:
        form = DocumentForm()

    return render(request, 'upload_document.html', {'form': form})

def document_list(request):
    documents = Document.objects.all()

    # Add file extension as metadata for each document
    for doc in documents:
        doc.file_extension = os.path.splitext(doc.file.url)[-1].lower()  # e.g., '.pdf', '.jpg'
    
    return render(request, 'document_list.html', {'documents': documents})
""" video"""
def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos})

def upload_videos(request):
    if request.method == 'POST':
        formset = VideoFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            messages.info(request, '*Upload successfully done*')
            #return redirect('pload_videos')  # Ensure this matches the name in urls.py
    else:
        formset = VideoFormSet(queryset=Video.objects.none())

    return render(request, 'upload_videos.html', {'formset': formset})


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import CourseContent, Quiz, Question, Option
from django.shortcuts import render, redirect, get_object_or_404
from .models import CourseContent, Quiz, Question, Option


def create_quiz(request, course_content_id):
    course_content = get_object_or_404(CourseContent, id=course_content_id)
    quiz_time_limit = request.POST.get('quiz_time_limit') or 10

    if request.method == 'POST':
        quiz_title = request.POST.get('quiz_title')
        quiz_description = request.POST.get('quiz_description')
        quiz = Quiz.objects.create(
            course_content=course_content,
            title=quiz_title,
            description=quiz_description,
            time_limit=quiz_time_limit
        )

        questions = request.POST.getlist('question[]')
        options = request.POST.getlist('option[]')
        correct_options = request.POST.getlist('correct_option[]')

        for i, question_text in enumerate(questions):
            question = Question.objects.create(
                quiz=quiz,
                question_text=question_text,
                marks=1
            )

            option_a = options[i * 4 + 0]
            option_b = options[i * 4 + 1]
            option_c = options[i * 4 + 2]
            option_d = options[i * 4 + 3]
            correct_option = correct_options[i]

            Option.objects.create(
                question=question,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option
            )

        return redirect('view_course', course_id=course_content.course.id)


    return render(request, 'create_quiz.html', {'course_content': course_content})
from django.shortcuts import render, get_object_or_404
from .models import Quiz, Question

from django.shortcuts import render, get_object_or_404
from .models import Quiz, Question
@login_required
def attempt_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    for question in questions:
        question.options = question.option_set.all()

    if request.method == 'POST':
        score = 0
        total_marks = 0 

        for question in questions:
            selected_answer = request.POST.get(f"question_{question.id}")
            correct_option = question.correct_option

            if selected_answer and selected_answer.upper() == correct_option.upper():
                score += question.marks
            total_marks += question.marks

        percentage = (score / total_marks) * 100 if total_marks > 0 else 0
        percentage = round(percentage, 2)

        # ✅ Save progress here!
        course_content = quiz.course_content
        course = course_content.course
        student = request.user

        try:
            enrollment = Enrollment.objects.get(course=course, student=student)
        except Enrollment.DoesNotExist:
            enrollment = None

        if enrollment:
            progress, created = StudentCourseProgress.objects.get_or_create(
                enrollment=enrollment,
                course_content=course_content
            )
            progress.quiz_score = percentage
            progress.save()
            print("✅ Progress saved:", percentage)

        return render(request, 'submit_quiz.html', {
            'score': score,
            'quiz': quiz,
            'percentage': percentage,
            'total_marks': total_marks,
            'course_id': course.id
        })

    return render(request, 'attempt_quiz.html', {'quiz': quiz, 'questions': questions})


def quiz_list(request):
    quizzes = Quiz.objects.all()  # Get all quizzes from the database
    return render(request, 'quiz_list.html', {'quizzes': quizzes})

from .models import StudentCourseProgress, Enrollment
@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()

    score = 0
    total_marks = 0

    for question in questions:
        selected_answer = request.POST.get(f"question_{question.id}")
        correct_answer = question.correct_option  # ✅ FIXED

        if selected_answer == correct_answer:
            score += question.marks
        total_marks += question.marks

    percentage = (score / total_marks) * 100 if total_marks > 0 else 0
    percentage = round(percentage, 2)

    course_content = quiz.course_content
    course = course_content.course
    student = request.user

    try:
        enrollment = Enrollment.objects.get(course=course, student=student)
    except Enrollment.DoesNotExist:
        enrollment = None

    if enrollment:
        progress, created = StudentCourseProgress.objects.get_or_create(
            enrollment=enrollment,
            course_content=course_content
        )
        progress.quiz_score = percentage
        progress.save()

    return render(request, 'submit_quiz.html', {
        'score': score,
        'quiz': quiz,
        'percentage': percentage,
        'total_marks': total_marks,
        'course_id': course.id
    })



from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from .models import Course

@login_required
def teacher_dashboard_view(request):
    teacher = request.user
    query = request.GET.get('q')  # Capture search input

    # Get courses created by the teacher
    courses = Course.objects.filter(teacher=teacher)

    # Apply search filtering if query exists
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'teacher_dashboard.html', {
        'courses': courses,
        'teacher_name': teacher.get_full_name() or teacher.username,
        'query': query  # Optional: to show "Results for..." in template
    })

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Course

@login_required
def add_course(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        thumbnail = request.FILES.get('thumbnail')  # Get uploaded file if any

        course = Course(
            title=title,
            description=description,
            teacher=request.user
        )

        if thumbnail:
            course.thumbnail = thumbnail

        course.save()
        return redirect('teacher_dashboard')

    return render(request, 'add_course.html')



@login_required
def add_course_content(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        title = request.POST['title']
        video = request.FILES.get('video')
        material = request.FILES.get('material')
        description = request.POST.get('description')
        CourseContent.objects.create(course=course, title=title, video=video, material=material, description=description)
        return redirect('teacher_dashboard')
    return render(request, 'add_course_content.html', {'course': course})
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, StudentCourseProgress, CourseContent

@login_required
def student_dashboard_view(request):
    query = request.GET.get('q')  # Get search term from search bar

    # Fetch all courses (filtered by search if applicable)
    courses = Course.objects.all()
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(teacher__first_name__icontains=query) |
            Q(teacher__last_name__icontains=query)
        )

    # Fetch enrollments for the current student
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    enrolled_courses = []

    for enrollment in enrollments:
        course = enrollment.course
        total_contents = CourseContent.objects.filter(course=course).count()
        completed_contents = StudentCourseProgress.objects.filter(enrollment=enrollment, is_completed=True).count()
        can_download_certificate = total_contents > 0 and completed_contents == total_contents  # ✅ Certificate eligibility check

        enrolled_courses.append({
            'course': course,
            'can_download_certificate': can_download_certificate
        })

    return render(request, 'student_dashboard.html', {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
        'student_name': request.user.get_full_name() or request.user.username,
        'query': query  # Needed to display search term in UI
    })

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect('student_dashboard')

from django.shortcuts import get_object_or_404, render
from .models import Course, CourseContent, Enrollment, StudentCourseProgress

@login_required
def view_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    content = course.coursecontent_set.all().order_by('id')

    is_enrolled = False
    enrollment = None
    student_progress = {}

    if hasattr(request.user, 'student'):
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None
        
        if enrollment:
            # Fetch student progress for each content item
            for item in content:
                student_progress[item.id] = item.studentcourseprogress_set.filter(enrollment=enrollment, is_completed=True).exists()

    return render(request, 'view_course.html', {
        'course': course,
        'content': content,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'student_progress': student_progress,
    })





@login_required
def view_course_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course)
    return render(request, 'course_students.html', {'course': course, 'enrollments': enrollments})


from django.contrib import messages

@login_required
def delete_course_content(request, content_id):
    content = get_object_or_404(CourseContent, id=content_id)
    
    # Optional: Check if the logged-in user is the course teacher
    if content.course.teacher != request.user:
        messages.error(request, "You are not authorized to delete this content.")
        return redirect('teacher_dashboard')
    
    course_id = content.course.id
    content.delete()
    messages.success(request, "Course content deleted successfully.")
    return redirect('view_course', course_id=course_id)


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    course.delete()
    return redirect('teacher_dashboard')


from django.shortcuts import render
from .models import Enrollment, StudentCourseProgress

def student_progress_view(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    progress_data = []

    for enrollment in enrollments:
        course = enrollment.course
        total_days = course.coursecontent_set.count()
        completed_days = StudentCourseProgress.objects.filter(enrollment=enrollment, is_completed=True).count()
        progress_percent = int((completed_days / total_days) * 100) if total_days > 0 else 0

        # ✅ Fetch quiz scores from StudentCourseProgress
        progress_records = StudentCourseProgress.objects.filter(enrollment=enrollment).exclude(quiz_score__isnull=True)
        quiz_scores = [p.quiz_score for p in progress_records]
        quiz_avg = round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else 0

        status = "Completed" if progress_percent == 100 else "Ongoing"

        progress_data.append({
            "student": request.user.get_full_name() or request.user.username,
            "course": course.title,
            "completed_days": f"{completed_days}/{total_days}",
            "progress": f"{progress_percent}%",
            "quiz_avg": f"{quiz_avg}%",
            "status": status,
        })

    return render(request, 'student_progress.html', {'progress_data': progress_data})

from django.shortcuts import render
from .models import Course, Enrollment, StudentCourseProgress

def teacher_course_progress_view(request):
    courses = Course.objects.filter(teacher=request.user)
    progress_data = []

    for course in courses:
        enrollments = Enrollment.objects.filter(course=course)
        total_days = course.coursecontent_set.count()

        for enrollment in enrollments:
            student = enrollment.student
            completed_days = StudentCourseProgress.objects.filter(enrollment=enrollment, is_completed=True).count()
            progress_percent = int((completed_days / total_days) * 100) if total_days > 0 else 0

            # ✅ Fetch quiz scores from StudentCourseProgress
            progress_records = StudentCourseProgress.objects.filter(enrollment=enrollment).exclude(quiz_score__isnull=True)
            quiz_scores = [p.quiz_score for p in progress_records]
            quiz_avg = round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else 0

            status = "Completed" if progress_percent == 100 else "Ongoing"

            progress_data.append({
                "student_name": student.get_full_name() or student.username,
                "course": course.title,
                "completed_days": f"{completed_days}/{total_days}",
                "progress": f"{progress_percent}%",
                "quiz_avg": f"{quiz_avg}%",
                "status": status,
            })

    return render(request, 'teacher_progress.html', {'progress_data': progress_data})

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import StudentCourseProgress, CourseContent, Enrollment

@login_required
def mark_as_complete(request, content_id):
    if request.method == 'POST':
        course_content = get_object_or_404(CourseContent, id=content_id)
        
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course_content.course)
        except Enrollment.DoesNotExist:
            return redirect('view_course', course_id=course_content.course.id)

        progress, created = StudentCourseProgress.objects.get_or_create(
            enrollment=enrollment,
            course_content=course_content
        )

        progress.is_completed = True
        progress.save()

    return redirect('view_course', course_id=course_content.course.id)

@login_required
def teacher_course_list_view(request):
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'teacher_progress_courses.html', {'courses': courses})
@login_required
def enrolled_students_view(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    enrollments = Enrollment.objects.filter(course=course)
    return render(request, 'teacher_progress_students.html', {
        'course': course,
        'enrollments': enrollments
    })

@login_required
def student_course_progress_view(request, course_id, student_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    student = get_object_or_404(User, id=student_id)
    enrollment = get_object_or_404(Enrollment, course=course, student=student)
    
    content_list = CourseContent.objects.filter(course=course)
    progress_data = []

    for content in content_list:
        progress = StudentCourseProgress.objects.filter(
            enrollment=enrollment,
            course_content=content
        ).first()

        progress_data.append({
            "title": content.title,
            "is_completed": progress.is_completed if progress else False,
            "quiz_score": progress.quiz_score if progress else None,
        })

    return render(request, 'teacher_student_progress_detail.html', {
        'student': student,
        'course': course,
        'progress_data': progress_data,
    })


from django.contrib.auth.decorators import login_required
from .models import Enrollment

@login_required
def student_my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    enrolled_courses = []

    for enrollment in enrollments:
        course = enrollment.course
        total_contents = course.coursecontent_set.count()
        completed_contents = StudentCourseProgress.objects.filter(enrollment=enrollment, is_completed=True).count()
        can_download_certificate = total_contents > 0 and completed_contents == total_contents

        enrolled_courses.append({
            'course': course,
            'can_download_certificate': can_download_certificate
        })

    return render(request, 'student_my_courses.html', {
        'courses': enrolled_courses,
        'student_name': request.user.get_full_name() or request.user.username
    })



from django.http import HttpResponse, FileResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from django.http import FileResponse, HttpResponse
from django.contrib.staticfiles import finders  # ✅ For logo/signature
from io import BytesIO
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import Course, CourseContent, Enrollment, StudentCourseProgress  # ✅ Add your models

def generate_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user

    # Check enrollment & completion
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if not enrollment:
        return HttpResponse("You are not enrolled in this course.")

    total_contents = CourseContent.objects.filter(course=course).count()
    completed_contents = StudentCourseProgress.objects.filter(enrollment=enrollment, is_completed=True).count()

    if total_contents == 0 or completed_contents < total_contents:
        return HttpResponse("You have not completed the course yet.")

    # ✅ Generate PDF
    square_size = 600  # Points (800x800 = ~11in x 11in)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(square_size, square_size))
    width = height = square_size

    # Colors and styles
    border_color = HexColor("#4CAF50")
    text_color = HexColor("#333333")
    title_color = HexColor("#2E86C1")

    # Draw Border
   # ✅ Draw Custom Background with Border Design
    background_path = finders.find("images/certificate_template.png")
    if background_path:
       c.drawImage(background_path, 0, 0, width=width, height=height, mask='auto')


    # ✅ Add LMS Logo
    logo_path = finders.find("images/lms_logo.png")
    if logo_path:
        c.drawImage(logo_path, width/2 - 50, height - 180, width=120, height=80, mask='auto')

    # Title
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(title_color)
    c.drawCentredString(width / 2, height - 220, "Certificate of Completion")

    # Subtitle
    c.setFont("Helvetica", 16)
    c.setFillColor(text_color)
    c.drawCentredString(width / 2, height - 260, "This is to certify that")

    # Student Name
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 290, f"{student.get_full_name() or student.username}")

    # Completion Text
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 330, f"has successfully completed the course")

    # Course Name
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(title_color)
    c.drawCentredString(width / 2, height - 370, f"{course.title}")
    signature_path = finders.find("images/signature.png")
       # Instructor Signature - Bottom Right
    if signature_path:
        c.drawImage(signature_path, width - 180, 125, width=120, height=20, mask='auto')
    c.line(width - 200, 120, width - 60, 120)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width - 130, 100, "Instructor Signature")

    # Date of Completion Section - Bottom Left (Styled like signature)
    c.line(60, 120, 200, 120)
    c.setFont("Helvetica", 12)
    c.drawCentredString(130, 100, "Date of Completion")

    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(text_color)
    c.drawCentredString(130, 130, datetime.now().strftime('%B %d, %Y'))

    # LMS Footer
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(HexColor("#888888"))
    c.drawCentredString(width / 2, 60, "Generated by LMS · Learn. Grow. Achieve.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"{course.title}_Certificate.pdf")


from .models import Course, CourseReview, Enrollment
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def submit_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Ensure student is enrolled and completed the course
    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
    if not enrollment:
        return HttpResponse("You are not enrolled in this course.")

    total = course.coursecontent_set.count()
    completed = enrollment.studentcourseprogress_set.filter(is_completed=True).count()
    if completed < total:
        return HttpResponse("You need to complete the course before reviewing.")

    if request.method == 'POST':
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback')

        CourseReview.objects.update_or_create(
            course=course,
            student=request.user,
            defaults={'rating': rating, 'feedback': feedback}
        )
        return redirect('student_dashboard')

    return render(request, 'submit_review.html', {'course': course})

##
from .models import CourseAnswer,CourseQuestion
@login_required
def course_forum(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = course.questions.all().order_by('-created_at')

    if request.method == 'POST':
        question_text = request.POST.get('question')
        if question_text:
            CourseQuestion.objects.create(course=course, student=request.user, question_text=question_text)
            return redirect('course_forum', course_id=course.id)

    return render(request, 'course_forum.html', {'course': course, 'questions': questions})


@login_required
def post_answer(request, question_id):
    question = get_object_or_404(CourseQuestion, id=question_id)
    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        if answer_text:
            CourseAnswer.objects.create(question=question, user=request.user, answer_text=answer_text)
    return redirect('course_forum', course_id=question.course.id)


@login_required
def vote_item(request, type, obj_type, obj_id):
    model = CourseQuestion if obj_type == "question" else CourseAnswer
    obj = get_object_or_404(model, id=obj_id)
    if type == "upvote":
        obj.upvotes += 1
    else:
        obj.downvotes += 1
    obj.save()
    return redirect('course_forum', course_id=obj.question.course.id if obj_type == "answer" else obj.course.id)



