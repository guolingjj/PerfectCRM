from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import timedelta, datetime
from myadmin.utils import paginator

register = template.Library()


@register.simple_tag
def showfilter(models_obj, filter_dict):
    select_str = ""
    if hasattr(models_obj, 'model'):
        for k in models_obj.list_filter:
            selected = ""
            field_obj = models_obj.model._meta.get_field(k)
            if type(field_obj).__name__ in ("DateTimeField", "DateField"):

                select_str += "<div class='col-lg-2 '><select class='form-control input-sm m-bot15 ' name='%s__gte_exact' >" % k
            else:
                select_str += "<div class='col-lg-2 '><select class='form-control input-sm m-bot15 ' name='%s_exact' >" % k

            if field_obj.choices:
                select_str += "<option value=''>----%s----</option>"% models_obj.model._meta.get_field(k).verbose_name
                for i in field_obj.choices:
                    if filter_dict.get(k) == str(i[0]):
                        selected = 'selected'
                    select_str += "<option value='%s' %s>%s</option>" % (i[0], selected, i[1])
                    selected = ""
            elif type(field_obj).__name__ in ("ForeignKey", "ManyToManyField"):
                F_M_list=field_obj.get_choices()
                F_M_list.pop(0)
                select_str += "<option value=''>----%s----</option>" % models_obj.model._meta.get_field(k).verbose_name
                for i in F_M_list:

                    if filter_dict.get(k) == str(i[0]):
                        selected = 'selected'
                    select_str += "<option value='%s' %s>%s</option>" % (i[0], selected, i[1])
                    selected = ""
            elif type(field_obj).__name__ in ("DateTimeField", "DateField"):

                today = datetime.now().date()
                yestodays = today - timedelta(days=1)
                yes7days = today - timedelta(days=7)
                mtd = today.replace(day=1)
                yes30days = today - timedelta(days=30)
                mty = mtd.replace(month=1)
                data_list = []
                data_list.append(["今天", today])
                data_list.append(["昨天", yestodays])
                data_list.append(["近7天", yes7days])
                data_list.append(["本月", mtd])
                data_list.append(["近30天", yes30days])
                data_list.append(["今年", mty])
                select_str += "<option value=''>----%s----</option>" % models_obj.model._meta.get_field(k).verbose_name
                for i in data_list:
                    if filter_dict.get(k + "__gte") == str(i[1]):
                        selected = 'selected'
                    select_str += "<option value='%s' %s>%s</option>" % (i[1], selected, i[0])
                    selected = ""


            else:
                select_str += "<option value=''>----%s----</option>" % models_obj.model._meta.get_field(k).verbose_name
                for i in models_obj.model.objects.all().values_list(k):
                    if filter_dict.get(k) == str(i[0]):
                        selected = 'selected'
                    select_str += "<option value='%s' %s>%s</option>" % (i[0], selected, i[0])
                    selected = ""
            select_str += "</select></div>"
    return mark_safe(select_str)


@register.simple_tag
def get_horizontal_option(horizontal, models_obj):
    temp = getattr(models_obj.model, horizontal)
    return temp.rel.model.objects.all()


@register.simple_tag
def get_selected_horizontal_option(horizontal, models_obj, id):
    cur_obj = models_obj.model.objects.get(id=id)
    horizontal_obj = getattr(cur_obj, horizontal)
    return horizontal_obj.get_queryset()
@register.simple_tag
def handle_related_obj(objs):
    '''获取当前models关系类'''
    ul_ele="<ul>"
    #---------获取没m2m关系
    """
    obj._meta.verbose_name 设置的verbose_name
    obj._meta.local_many_to_many 或者对象的直接关联的m2m对象list
    obj.slect_related() == all()
    obj._meta.related_objects  获取到所有的联系对象,包括m2m的list
    obj.get_accessor_name()  获取该字段的反向查询   默认是 字段__set
    
    
    """
    li_ele=""
    sub_ul_ele=''
    for obj in objs:
        li_ele = "<li>%s:%s</li>"%(obj._meta.verbose_name,obj.__str__().strip('<>'))
        ul_ele += li_ele
        for i in obj._meta.local_many_to_many:
            sub_ul_ele="<ul>"
            m2m_field=getattr(obj,i.name)#(models.table)
            for o in m2m_field.select_related():
                li_ele='<li>%s:%s</li>'%(i.verbose_name, o.__str__().strip("<>"))
                sub_ul_ele+=li_ele
            sub_ul_ele+="</ul>"
        ul_ele+=sub_ul_ele

    for related_obj in obj._meta.related_objects:
        if 'ManyToManyRel' in related_obj.__repr__():
            if hasattr(obj,related_obj.get_accessor_name()):
                access_obj=getattr(obj,related_obj.get_accessor_name())
                if hasattr(access_obj,"select_related"):
                    target_objs=access_obj.select_related()
                    sub_ul_ele="<ul style='color:bule'>"
                    for o in target_objs:
                        li_ele = '<li>%s:%s</li>' % (o._meta.verbose_name, o.__str__().strip("<>"))
                        sub_ul_ele += li_ele
                    sub_ul_ele += "</ul>"
                    ul_ele += sub_ul_ele
        elif hasattr(obj,related_obj.get_accessor_name()):
            access_obj=getattr(obj,related_obj.get_accessor_name())
            if hasattr(access_obj,"select_related"):
                target_objs=access_obj.select_related()
            else:#one to one
                target_objs = access_obj
            if len(target_objs)>0:
                _next_response=handle_related_obj(target_objs)
                ul_ele+=_next_response

    ul_ele+='</ul>'
    return mark_safe(ul_ele)

@register.simple_tag
def get_objs_id(objs):
    d_id=""
    for i in objs:
        d_id+="-"+str(i.id)
    return d_id.strip("-")
@register.simple_tag
def get_verbose_name(obj):
    if hasattr(obj,'model'):
        return obj.model._meta.verbose_name
    else:
        return obj._meta.verbose_name

@register.simple_tag
def hanle_menu(user_obj):
    role_queryset=user_obj.role.all()
    menu_list=[]
    for role in role_queryset:
        for menu_obj in role.menus.all():
            if menu_obj not in menu_list:
                menu_list.append(menu_obj)

    return menu_list