from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=128,null=True, blank=True)
    role_type = models.CharField(max_length=10, default="student")
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg') # ✅ Added
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")],default="Male")
    college = models.CharField(max_length=200, null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)
    current_address = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
     
    
    def __str__(self):
        return self.username

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=128,null=True, blank=True)
    role_type = models.CharField(max_length=10, default="teacher")
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")],default="Male")
    college = models.CharField(max_length=200, null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)
    current_address = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username
class Education(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name="educations")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name="educations")
    institution_name = models.CharField(max_length=255,null=True, blank=True)
    degree = models.CharField(max_length=255,null=True, blank=True)
    field_of_study = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=50, blank=True, null=True)
    institution_logo = models.ImageField(upload_to="education_logos/", blank=True, null=True)  # Optional logo field
    def __str__(self):
        return self.institution_name
    
class Internship(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name="internships")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name="internships")
    company_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.company_name} - {self.role}"


class Skill(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True,related_name="skills")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name="skills")
    name = models.CharField(max_length=100)


class Video(models.Model):
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')  # The file will be stored in 'MEDIA_ROOT/documents/'
    uploaded_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Quiz(models.Model):
    course_content = models.ForeignKey('CourseContent', on_delete=models.CASCADE, related_name='quizzes',null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    marks = models.IntegerField(default=1)  # Ensure this field exists in your model
    
    # Add any other fields here

    def __str__(self):
        return self.title

class Question(models.Model):
    question_text = models.TextField()
    marks = models.IntegerField(default=1)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default="A")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return f"Question {self.id} for {self.quiz.title}"

class Option(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    option_a = models.CharField(max_length=255, default="Default Option")
    option_b = models.CharField(max_length=255, default="Default Option")
    option_c = models.CharField(max_length=255, default="Default Option")
    option_d = models.CharField(max_length=255, default="Default Option")
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default="A")

    def __str__(self):
        return f"Options for: {self.question.question_text}"


class StudentAnswer(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Update to reference the custom user model
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)

    def __str__(self):
        return f"Answer by {self.student} for {self.question}"


from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    num_lectures = models.IntegerField(default=0)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)  # New


    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

class CourseContent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # e.g. "Day 1"
    video = models.FileField(upload_to='videos/',max_length=255, blank=True, null=True)
    material = models.FileField(upload_to='materials/',max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"
