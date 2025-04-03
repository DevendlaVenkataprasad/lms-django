from django.contrib import admin
from .models import Student, Teacher, Education, Internship, Skill

class EducationInline(admin.TabularInline):  
    model = Education
    extra = 1  # Show one empty form for quick addition

class InternshipInline(admin.TabularInline):  
    model = Internship
    extra = 1

class SkillInline(admin.TabularInline):  
    model = Skill
    extra = 1

class StudentAdmin(admin.ModelAdmin):
    list_display = ("get_username", "get_email")  # Fix username & email references
    search_fields = ("user__username", "user__email")  # Enable search by User model fields
    inlines = [EducationInline, InternshipInline, SkillInline]  # Show related models inside Student admin page

    def get_username(self, obj):
        return obj.user.username
    get_username.admin_order_field = "user__username"
    get_username.short_description = "Username"

    def get_email(self, obj):
        return obj.user.email
    get_email.admin_order_field = "user__email"
    get_email.short_description = "Email"

admin.site.register(Student, StudentAdmin)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("get_username", "get_email")
    search_fields = ("user__username", "user__email")
    inlines = [EducationInline, InternshipInline, SkillInline]

    def get_username(self, obj):
        return obj.user.username
    get_username.admin_order_field = "user__username"
    get_username.short_description = "Username"

    def get_email(self, obj):
        return obj.user.email
    get_email.admin_order_field = "user__email"
    get_email.short_description = "Email"
