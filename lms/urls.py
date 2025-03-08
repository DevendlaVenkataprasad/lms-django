from django.urls import path
from .views import profile_view,chatbot_response,student_dashboard_view, teacher_dashboard_view,send_otp,home_view,login_view, register_view, logout_view, forgot_password_view,reset_password_view,verify_otp

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('',home_view,name='home'),
    path('reset-password/<int:user_id>/<str:token>/', reset_password_view, name='reset_password'),
    path('verify_otp',verify_otp,name='verify_otp'),
     path('send-otp/', send_otp, name='send_otp'),  # ✅ Add this line
     path("student-dashboard/", student_dashboard_view, name="student_dashboard"),
    path("teacher-dashboard/", teacher_dashboard_view, name="teacher_dashboard"),
    path("chatbot/", chatbot_response, name="chatbot_response"),
     path("profile/", profile_view, name="profile"),
]
