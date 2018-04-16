from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from crm import forms
from crm import models
import random
import string
from django.core.cache import cache
import os
from PerfectCRM import settings
# Create your views here.
@login_required
def index(req):
    print(req.user.get_username())
    return render(req,'blank.html')
def custom_list(req):
    return render(req, 'sales/sales_index.html')

def acc_login(req):
    error=''

    if req.method=="GET":
        return render(req,"login.html")
    else:

        _email=req.POST.get("acc")
        _pwd=req.POST.get("pwd")
        user=authenticate(username=_email,password=_pwd)#验证:返回验证对象,失败则是None

        if user:
            login(req,user)
            next_url = req.GET.get("next", '../index')
            return redirect(next_url)
        else:
            error="账号或者密码错误"
            return render(req, "login.html",{'error':error})

def acc_logout(req):
    logout(req)
    return redirect("/crm/acc_login")

def enrollment(req, table_name, id):
    customer=models.Customer.objects.get(id=id)
    msg = ''
    random_str = ''.join(random.sample(string.ascii_lowercase + string.digits, 8))


    #决定报名,生成报名表
    if customer.status == 1:
        cache.set(customer.enrollment_set.last().id, random_str, 6000)
        msg = "localhost:8090/crm/customer/%s/registration/%s" % (customer.enrollment_set.last().id, random_str)

        return render(req, 'sales/enrollment.html', { "customer": customer, 'msg':msg})
    #学生已填写报名表,审核
    if customer.status == 2:

        customer_form_obj=forms.Customerform(instance=customer)
        return render(req, 'sales/enrollment.html', {'customer_form_obj': customer_form_obj,'customer':customer})
    if req.method=="GET":
        mf=forms.Enrollmentmodelform()
        return render(req, 'sales/enrollment.html', {'mforms_obj': mf, "customer": customer,})
    if req.method == "POST":

        mf = forms.Enrollmentmodelform(req.POST)
        if mf.is_valid():



            try:
                mf.cleaned_data['customer']=customer
                cur_enroll_obj = models.Enrollment.objects.create(**mf.cleaned_data)
                if customer.status == 4:
                    models.Payment.objects.create(**{
                        "customer": customer,
                        "consultant": customer.consultant,
                        'pay_course': customer.consult_course
                    })
                    return HttpResponse('缴费表已生成,请提醒学生前往缴费')
                else:
                    customer.status=1
                    customer.save()
                    cache.set(customer.enrollment_set.last().id, random_str, 6000)
                    msg = "localhost:8090/crm/customer/%s/registration/%s" % (customer.enrollment_set.get().id, random_str)

            except IntegrityError as e:

                mf.add_error('__all__',"重复创建报名信息,请重写")
                print(mf.errors)


        return render(req, 'sales/enrollment.html', {'mforms_obj': mf, "customer": customer,'msg':msg})



def enrollmentConfirm(req, table_name, id):
    customer = models.Customer.objects.get(id=id)
    msg = ''
    random_str = ''.join(random.sample(string.ascii_lowercase + string.digits, 8))
    if req.GET.get('pass') == '2':

        customer.status = 1
        customer.save()
        cache.set(customer.enrollment_set.last().id, random_str, 6000)
        msg = "localhost:8090/crm/customer/%s/registration/%s" % (customer.enrollment_set.get().id, random_str)

        return redirect('/crm/customer/%s/enrollment/'%id, {"customer": customer, 'msg': msg})
    else:
        #审核通过,吧报名表的审核状态修改成已经审核了
        customer.status = 3
        customer.save()

        models.Payment.objects.create(**{
            "customer": customer,
            "consultant": customer.consultant,
            'pay_course': customer.consult_course
        })
        return redirect('/crm/customer/%s/enrollment/'%id, {"customer": customer})


def stu_registration(req,id,str):
    enroll_obj=models.Enrollment.objects.get(id=id)
    if req.is_ajax():
        print(req.FILES)
        enroll_obj_dir = '%s/%s' % (settings.CUSTOMER_ID_DATA_URL, id)
        if not (os.path.exists(enroll_obj_dir)):
            os.makedirs(enroll_obj_dir, exist_ok=True)
        for k,v in req.FILES.items():
            with open('%s/%s'%(enroll_obj_dir,v.name),'wb') as f:
                for chunk in v.chunks():
                    f.write(chunk)

    if cache.get(id)==str:
        if req.method=="GET":

            coustomer_form = forms.Customerform(instance=enroll_obj.customer)
            return render(req,'sales/stu_registration.html',{'coustomer_form':coustomer_form,'enroll_obj':enroll_obj})
        elif req.method == "POST":
            coustomer_form = forms.Customerform(req.POST,instance=enroll_obj.customer)
            if coustomer_form.is_valid():
                enroll_obj.customer.status=2
                enroll_obj.customer.save()
                coustomer_form.save()

                enroll_obj.contract_agreed=True
                enroll_obj.save()
                return render(req, 'sales/stu_registration.html',
                              {'coustomer_form': coustomer_form, 'enroll_obj': enroll_obj})
            else:
                return render(req, 'sales/stu_registration.html',
                              {'coustomer_form': coustomer_form, 'enroll_obj': enroll_obj})
    else:
        return HttpResponse('连接已经失效')



def create_student(req,customer_id):
    customer_obj=models.Customer.objects.get(id=customer_id)


    default_password=customer_obj.id_num[-6::1]
    role=models.Role.objects.get(name='学生')


    obj=models.UserProfile.objects.create_user(customer_obj.email,customer_obj.name,customer_obj,default_password)
    obj.role.add(role)
    obj.save()
    customer_obj.status = 4
    customer_obj.save()
    return HttpResponse('客户已成为学员,账号为所留邮箱,密码为身份证后6位....')



def forms_test(request):
    from django.shortcuts import render, redirect
    from crm.myforms import MyForm


    if request.method == "GET":
        print('111111111')
        obj = MyForm()
        return render(request, 'blank.html', {'form': obj})
    elif request.method == "POST":
        obj = MyForm(request.POST, request.FILES)
        if obj.is_valid():
            values = obj.clean()
            print(values)
        else:
            errors = obj.errors
            print(errors)
        return render(request, 'formsindex.html', {'form': obj})
    else:
        return redirect('http://www.baidu.com')