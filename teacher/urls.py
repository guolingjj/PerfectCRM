from django.contrib import admin
from django.urls import path,include
from teacher import views
urlpatterns = [
    path('teacher_index/', views.teacher_index,name='teacher_index'),
    path('down_homework/<int:stu_record_id>', views.down_homework),
    path('teacher_courserecord/<str:class_id>/<int:stu_record_id>', views.teacher_courserecord,name='teacher_courserecord'),
    path('teacher_courserecord/<str:class_id>/add', views.teacher_courserecord_add,name='teacher_courserecord_add'),



]