from django.db import models
from django.contrib.auth.models import User

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
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.company_name} - {self.role}"


class Skill(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True,related_name="skills")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True, related_name="skills")
    name = models.CharField(max_length=100)


