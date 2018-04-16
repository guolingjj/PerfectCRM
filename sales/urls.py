from django.contrib import admin
from django.urls import path,include
from sales import views
urlpatterns = [
    path('sales_index/', views.sales_index,name='sales_index'),
    path('sales_all_customer/', views.sales_all_customer,name='sales_all_customer'),
    path('sales_customerfollowup/', views.sales_customerfollowup,name='customer_follow_up'),


]