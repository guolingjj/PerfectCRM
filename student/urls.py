from django.contrib import admin
from django.urls import path,include,re_path
from student import views
urlpatterns = [
    path('student_index/', views.student_index,name='student_index'),

    path('<str:enrollment_id>/course_record/', views.course_record,name='course_record'),

    path('<str:studyrecord_id>/homework/down/<str:name>', views.hm_file_down,name='homework_down'),
    re_path(r'\d+/course_record/(?P<studyrecord_id>\w+)/homework$',views.stu_submit_homework,name='stu_submit_homework'),

]