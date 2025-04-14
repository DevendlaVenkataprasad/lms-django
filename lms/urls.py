from django.urls import path
from .views import   student_my_courses,student_course_progress_view,enrolled_students_view,teacher_course_list_view,mark_as_complete,student_progress_view,teacher_course_progress_view,delete_course,view_course_students,delete_course_content,view_course,enroll_course,add_course_content,add_course,document_list,view_all,add_content,upload_videos,video_list,create_quiz,quiz_list,attempt_quiz,submit_quiz,upload_document,save_internship,delete_internship,delete_education,upload_profile_picture,edit_education,edit_profile,update_profile,profile_view,chatbot_response,student_dashboard_view, teacher_dashboard_view,send_otp,home_view,login_view, register_view, logout_view, forgot_password_view,reset_password_view,verify_otp

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
      path("update_profile/", update_profile, name="update_profile"),
      path("edit_profile/", edit_profile, name="edit_profile"),
       path('delete-education/<int:education_id>/', delete_education, name='delete_education'),
      path('upload_profile_picture/', upload_profile_picture, name='upload_profile_picture'),
   
    path('edit-education/', edit_education, name='edit_education'),
    path("save-internship/", save_internship, name="save_internship"),
    path('delete-internship/<int:internship_id>/', delete_internship, name="delete_internship"),
    

    path('upload-document/', upload_document, name='upload_document'),
    path('document-list/', document_list, name='document_list'),
    path('view_all/',view_all,name='view_all'),
    path('add_content/',add_content,name='add_content'),

    path('upload-videos/', upload_videos, name='upload_videos'),
    path('video-list/', video_list, name='video_list'),

    
    path('course_content/<int:course_content_id>/quiz/create/', create_quiz, name='create_quiz'),
    path('quizzes/',quiz_list,name='quiz_list'),
    path('quiz/', quiz_list, name='quiz_list'),  # Add this line
    path('quiz/<int:quiz_id>/attempt/', attempt_quiz, name='attempt_quiz'),
    path('quiz/<int:quiz_id>/submit/', submit_quiz, name='submit_quiz'),  



    path('add_course/', add_course, name='add_course'),
    path('course/<int:course_id>/add_content/', add_course_content, name='add_course_content'),

    path('course/<int:course_id>/enroll/', enroll_course, name='enroll_course'),
    path('course/<int:course_id>/', view_course, name='view_course'),
    path('content/<int:content_id>/delete/', delete_course_content, name='delete_course_content'),
    path('course/<int:course_id>/students/', view_course_students, name='course_students'),
    path('delete_course/<int:course_id>/', delete_course, name='delete_course'),
    path('student/progress/', student_progress_view, name='student_progress'),
    path('teacher/progress/', teacher_course_progress_view, name='teacher_progress'),
    path('course/mark-complete/<int:content_id>/', mark_as_complete, name='mark_as_complete'),
    path('teacher/progress/', teacher_course_list_view, name='teacher_progress'),
    path('teacher/progress/<int:course_id>/', enrolled_students_view, name='course_students_progress'),

    path('teacher/progress/<int:course_id>/student/<int:student_id>/', student_course_progress_view, name='student_course_progress'),
    path('student/my-courses/', student_my_courses, name='student_my_courses'),


]