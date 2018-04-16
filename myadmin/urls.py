from django.contrib import admin
from django.urls import path,include,re_path
from myadmin import views
urlpatterns = [
    path('admin_index/', views.admin_index),
    # re_path(r'<str:app_name>/<str:table_name>/<str:group>', views.data_show,name="models_data"),
    re_path(r'^(?P<app_name>\w+)/(?P<table_name>\w+)/(?P<own>[o]?|\d{0,2})$',views.data_show,name="models_data"),
    path('<str:app_name>/<str:table_name>/<str:id>/change/', views.change_data,name='change_data'),
    path('<str:app_name>/<str:table_name>/<str:id>/delete/', views.delete_data,name='delete_data'),
    path('<str:app_name>/<str:table_name>/<str:id>/password_reset/', views.password_reset),
    path('<str:app_name>/<str:table_name>/add/', views.add_data,name='add_data'),
    path('<str:app_name>/<str:table_name>/action/', views.action_central),



]