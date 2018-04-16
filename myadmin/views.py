from django.shortcuts import render
from crm import models
from myadmin import kingadmin
from myadmin.utils import paginator, table_filter, order
from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Q
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
import re
from myadmin import Myforms
from crm.permission.permission_handle import check_permission
@login_required
def admin_index(req):
    obj = kingadmin.r_data
    return render(req, 'myadmin/myadmin.html', {'obj': obj})

@login_required
def data_show(req, app_name, table_name,own):
    models_data = kingadmin.r_data[app_name][table_name]

    if req.method == "POST":
        import json
        id_list = req.POST.get("id")
        action_method = req.POST.get("action")
        id_list = json.loads(id_list)
        op_obj = models_data.model.objects.filter(id__in=id_list).all()
        obj = models_data()
        method = getattr(obj, action_method)
        return method(req, op_obj)
    else:
        # 获取当前要处理的table对象
        cur_page = int(req.GET.get("p", 1))  # 默认为1,获取当前页码
        r_data = ""
        r_th = ""
        get_argument_dict = {}  # 所有的参数
        filter_condition = {}  # 过滤的参数
        order_condition = []  # 排序的参数
        p_url = ''
        filter_url = ''
        has_filter = False  # 是否有过滤
        has_order = False  # 是否有排
        has_search = [False, ""]  # 是否有查询
        q = Q()
        # 如果有自定制条件
        if hasattr(models_data, 'model'):
            v_name = models_data.model._meta.verbose_name
            models_data.vname = v_name

            # 将get请求的条件变成字典存储,判断是否有过滤条件和排序条件
            for k, v in req.GET.items():
                if "_exact" in k:
                    has_filter = True
                if k == "o":
                    has_order = True
                if k == "q":
                    has_search[0] = True

                get_argument_dict[k] = v


            # 如果有过滤条件
            if has_filter:
                filter_obj = table_filter.Filter_manage(get_argument_dict)

                filter_condition = filter_obj.get_filtered()

                filter_url = filter_obj.get_filter_url()

                p_url += filter_obj.get_filter_url()
            # 如果有排序条件

            if has_order:
                order_obj = order.Order_manage(get_argument_dict)

                order_condition = order_obj.get_order_list()

                p_url += order_obj.get_order_url()
            if has_search[0]:

                q.connector = "OR"
                for i in models_data.list_search:
                    q.children.append(("%s__contains" % i, get_argument_dict["q"]))
                p_url += "&q=%s" % get_argument_dict["q"]
                has_search[1] = get_argument_dict["q"]

            # 区分group
            if own=='o':


                filter_condition['consultant']=req.user.id
            role_name_list=[]
            cur_role=req.user.role.all()
            for role_obj in cur_role:
                role_name_list.append(role_obj.name)
                #对应上课记录的详情
            if table_name=='courserecord' and '老师' in role_name_list:
                if own:
                    filter_condition['clazz']=int(req.path.split('/')[-1])
                filter_condition['teachers'] = req.user.id
            if table_name=='studyrecord' and '老师' in role_name_list:
                if own:
                    filter_condition['course_record'] = int(req.path.split('/')[-1])






            data_list = models_data.model.objects.filter(**filter_condition).filter(q).order_by(*order_condition).all()

            data_count = data_list.count()

            p = paginator.pagemanage(5, data_count, cur_page,10, "myadmin/%s/%s" % (app_name, table_name))  # 使用自己写好的分页类
            pager = p.getpager(p_url)  # 获取最后返回的字符串,就是包含标签的字符串
            pageint = p.get_pageint()  # 获取到本次的显示页的起始数据和结束数据
            page_count = p.get_countpage  # 获取总共的页数

            r_th += "<th><input type='checkbox' val='%s' id='check-all'></th>"

            r_th_extra = ''
            r_td_extra = ''
            #******************如果有额外数据展示



            #**********************额外数据展示结束
            #如果有list_display:
            if getattr(models_data,'list_display'):


                for k in models_data.list_display:

                    # 处理排序字符串,o=自己的名字+过滤条件,不需要分页

                    if has_order and k == get_argument_dict["o"]:

                        r_th += "<th><a href='?o=-%s%s'>%s</a> <span class='glyphicon glyphicon-triangle-bottom'></span> </th>" % (
                            k, filter_url, models_data.model._meta.get_field(k).verbose_name)
                    elif has_order and "-" + k == get_argument_dict["o"]:
                        r_th += "<th><a href='?o=%s%s'>%s</a> <span class='glyphicon glyphicon-triangle-top'></span> </th>" % (
                            k, filter_url, models_data.model._meta.get_field(k).verbose_name)
                    else:
                        r_th += "<th><a href='?o=%s%s'>%s</a> </th>" % (k, filter_url, models_data.model._meta.get_field(k).verbose_name)







                if data_list:#如果有数据
                    if models_data.extra_fileds:
                        for k, v in models_data.extra_fileds.items():

                            r_th_extra += "<th>%s</th>" % k
                        r_th += r_th_extra
                #
                #             for i in (data_list[pageint[0]:pageint[1]]):
                #
                #                 extra_func = getattr(models_data, v)
                #
                #                 r_td_extra += "<td>%s</td>" % (
                #                 extra_func(models_data, req, i, k))# i是每条数据的对象row_obj,k是字段名字

                    for i in (data_list[pageint[0]:pageint[1]]):


                        r_data += "<tr>"


                        for k in models_data.list_display:

                            if k == models_data.list_display[0]:

                                current_arg = urlencode(get_argument_dict)

                                if i._meta.get_field(k).choices:
                                    r_data += "<td><input type='checkbox' val='%s' class='check-field'></td><td><a href='./%s/change/?%s'>%s</a></td>" % (
                                        i, id, i.id, current_arg, getattr(i, "get_%s_display" % k)())
                                elif type(getattr(i, k)).__name__ == "datetime":
                                    r_data += "<td><input type='checkbox' val='%s' class='check-field'></td><td><a href='./%s/change/?%s'>%s</a></td>" % (
                                        i.id, i.id, current_arg, getattr(i, k).strftime("%Y-%m-%d"))
                                else:
                                    r_data += "<td><input type='checkbox' val='%s' class='check-field'></td><td><a href='./%s/change/?%s'>%s</a></td>" % (
                                        i.id, i.id, current_arg, getattr(i, k))

                            else:
                                if i._meta.get_field(k).choices:
                                    r_data += "<td>%s</td>" % getattr(i, "get_%s_display" % k)()
                                elif type(getattr(i, k)).__name__ == "datetime":
                                    r_data += "<td>%s</td>" % getattr(i, k).strftime("%Y-%m-%d")
                                else:
                                    r_data += "<td>%s</td>" % getattr(i, k)

                        if models_data.extra_fileds:
                            for k, v in models_data.extra_fileds.items():
                                extra_func = getattr(models_data, v)
                                r_td_extra += "<td>%s</td>" % (extra_func(models_data, req, i, k))
                        r_data+=r_td_extra
                        r_td_extra=''

                        r_data += "</tr>"





                    data_str = r_th + r_data  # 返回给前端的数据字符串
                else:
                    data_str = "<tr><td>未查找到数据</td></tr>"
            else:

                r_th="<th></th>"
                if models_data.model.objects.all().count() < 1:
                    r_data = "<th>未查找到数据<th>"
                else:
                    for i in (models_data.model.objects.all()[pageint[0]:pageint[1]]):
                        r_data += "<tr><td><input type='checkbox' val='%s' class='check-field'></td><td><a href='./%s/change'>%s</a></td></tr>" % (
                            i.id, i.id, i.__str__())
                data_str = r_data
        else:
            v_name = models_data._meta.verbose_name
            models_data.vname = v_name
            data_count = models_data.objects.all().count()
            ##获取分页数据
            p = paginator.pagemanage(5, data_count, cur_page, 1, "myadmin/%s/%s" % (app_name, table_name))  # 使用自己写好的分页类
            pager = p.getpager()  # 获取最后返回的字符串,就是包含标签的字符串
            pageint = p.get_pageint()  # 获取到本次的显示页的起始数据和结束数据
            page_count = p.get_countpage
            if models_data.objects.all().count()<1:
                r_data="<th>未查找到数据<th>"
            else:
                r_th='<th></th>'
                for i in (models_data.objects.all()[pageint[0]:pageint[1]]):
                    r_data += "<tr><td><input type='checkbox' val='%s' class='check-field'><td><a href='./%s/change'>%s</a></td></tr>" % (
                        i.id,i.id,i.__str__())
            data_str =r_data
        return render(req, "myadmin/table_show_data.html", {"obj": models_data,
                                                      "page_set": pager,
                                                      "data_str": data_str,
                                                      "data_count": data_count,
                                                      "page_count": page_count,
                                                      "filter_dict": filter_condition,
                                                      "has_search": has_search
                                                      })





@login_required
def change_data(req, app_name, table_name, id):

    models_obj = kingadmin.r_data[app_name][table_name]
    readonly_fileds = []
    if hasattr(models_obj, "readonly_fileds"):
        readonly_fileds = models_obj.readonly_fileds
    filter_horizontal = []
    if hasattr(models_obj, "model"):
        model_obj = models_obj.model.objects.get(id=id)

        if hasattr(models_obj, "filter_horizontal"):
            filter_horizontal = models_obj.filter_horizontal

    else:
        model_obj = models_obj.objects.get(id=id)
    forms_list = Myforms.Create_forms_class(models_obj,readonly_fileds)

    if req.method == "GET":
        forms_obj = forms_list(instance=model_obj)

        return render(req, "myadmin/table_change.html",
                      {"obj": forms_obj, 'filter_horizontal': filter_horizontal, "models_obj": models_obj, "id": id})
    elif req.method == "POST":
        forms_obj = forms_list(req.POST, instance=model_obj)
        print('req.psot:',req.POST)
        if forms_obj.is_valid():
            forms_obj.save()

            s = re.sub(r"/\d+/change", "", req.path)

            return redirect(re.sub(r"/\d+/change", "", req.path))

    return render(req, "myadmin/table_change.html",
                  {"obj": forms_obj, 'filter_horizontal': filter_horizontal, "models_obj": models_obj, "id": id})




# @check_permission
@login_required
def add_data(req, app_name, table_name):
    filter_horizontal = []
    readonly_fileds=[]
    models_obj = kingadmin.r_data[app_name][table_name]


    if hasattr(models_obj, "model"):

        if hasattr(models_obj, "filter_horizontal"):
            filter_horizontal = models_obj.filter_horizontal

    forms_list = Myforms.Create_forms_class(models_obj,readonly_fileds)

    if req.method == "GET":
        forms_obj = forms_list()

        return render(req, "myadmin/table_add.html",
                      {"obj": forms_obj, 'filter_horizontal': filter_horizontal, "models_obj": models_obj})

    elif req.method == "POST":
        forms_obj = forms_list(req.POST)


        if forms_obj.is_valid():

            obj=forms_obj.save()
            cur_password=forms_obj.cleaned_data.get("password")
            if cur_password:

                obj.set_password(cur_password)
                obj.save()

            return redirect(req.path.replace("/add/", "/"))

    return render(req, "myadmin/table_add.html",
                  {"obj": forms_obj, 'filter_horizontal': filter_horizontal, "models_obj": models_obj})





@login_required
def delete_data(req, app_name, table_name, id):
    models_obj = kingadmin.r_data[app_name][table_name]
    comfirm=req.GET.get('delete','')
    id=id.split("_")
    wrong = []
    if hasattr(models_obj, "model"):
        current_obj = models_obj.model.objects.filter(id__in=id)
    else:
        current_obj = models_obj.objects.filter(id__in=id)

    if comfirm:
        if hasattr(models_obj,'readonly_table') and getattr(models_obj,'readonly_table',None) :


            wrong=["表%s:%s只读不能被删除"%(table_name,models_obj.model.objects.get(id=id).__str__()),]

            return render(req, 'myadmin/table_delete.html',{"current_obj" :current_obj,'wrong':wrong})
        else:
            if hasattr(models_obj, "model"):
                models_obj.model.objects.filter(id__in=id).delete()
            else:
                models_obj.objects.filter(id__in=id).delete()
            return redirect(re.sub(r"/\w+/delete.*", "", req.path))
    else:

        return render(req, 'myadmin/table_delete.html', {"current_obj" :current_obj,'wrong':wrong})





#暂时没有用到
def action_central(req, app_name, table_name):
    import json
    models_obj = kingadmin.r_data[app_name][table_name]
    id_list = req.POST.get("id_list")
    action_method = req.POST.get("action-method")
    id_list = json.loads(id_list)
    op_obj = models_obj.model.objects.filter(id__in=id_list).all()
    obj = models_obj()
    method = getattr(obj, action_method)
    return method(req, op_obj)




@login_required
def password_reset(req, app_name, table_name,id):
    if req.method=="GET":

        return render(req,"myadmin/password_reset.html")
    elif req.method=="POST":
        error=[]
        models_obj = kingadmin.r_data[app_name][table_name]
        if hasattr(models_obj,'model'):
            cur_obj=models_obj.model.objects.get(id=id)
            db_old_pwd=cur_obj.password
            input_old_pwd=req.POST.get("old-pwd")
            input_new_pwd=req.POST.get("new-pwd")
            input_confirm_pwd=req.POST.get("confirm-pwd")
            if input_new_pwd==input_confirm_pwd:
                if cur_obj.check_password(input_old_pwd):
                    if  len(input_confirm_pwd)<5 or len(input_confirm_pwd)>15:
                        error = ["新密码长度必须是6到14位", ]
                    elif  cur_obj.check_password(input_confirm_pwd):
                        error = ["新密码和旧密码一致,请修改", ]
                    else:
                        cur_obj.set_password(input_confirm_pwd)
                        cur_obj.save()
                        print(type(id))
                        print(type(req.user.id))
                        if req.user.id==int(id):
                            return redirect('/crm/acc_login')
                        else:
                            return redirect('../change')

                else:
                    error = ["旧密码不正确", ]
            else:
                error=["两次输入的密码不一致",]
            return render(req, "myadmin/password_reset.html",{'error':error})

        return render(req, "myadmin/password_reset.html")




