from django.shortcuts import render
from crm import views

# Create your views here.
def sales_index(req):
    return render(req,'sales/sales_index.html')
def sales_all_customer(req):

    return render(req,'sales/sales_all_customer.html')
def sales_customerfollowup(req):
    pass