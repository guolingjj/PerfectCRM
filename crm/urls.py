from django.contrib import admin
from django.urls import path,include
from crm import views
urlpatterns = [
    path('index/', views.index),
    path('testindex/', views.forms_test),
    path('acc_login/', views.acc_login),
    path('acc_logout/', views.acc_logout,name="acc_logout"),
    path('create_student/<int:customer_id>', views.create_student,name="create_student"),
    path('<str:table_name>/<str:id>/enrollment/', views.enrollment),
    path('<str:table_name>/<str:id>/enrollment/confirm/', views.enrollmentConfirm),
    path('customer/<str:id>/registration/<str:str>', views.stu_registration,name="stu_registration"),


]