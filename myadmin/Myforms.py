# from django import forms
# class Myforms(forms.ModelForm):
#     def __init__(self,mymodels):
#         super(Myforms,self).__init__()
#         self.mymodels=mymodels
#
#     class Meta:
#         def __init__(self,models_obj):
#             pass
#
#         fields="__all__"
#         model=Myforms.Myforms

from django import forms
from crm import models
from django.forms import widgets as ws
from django.forms import ValidationError
def Create_forms_class(models_obj,readonly_fileds):

    def __new__(cls,*args,**kwargs):
        '''通过new方法区给前段加上样式
        这里的__new__是要加入到动态创建的modelform类当中,
        cls代指的ModelForm类
        ModelForm类中有base_field{},存放着指定model类的字段

        ------加入单个字段验证-----
        查看_clean_fields()方法知道dajngo forms 为了们预留自定义验证单个字段的方法,在自己的界面自定义一个验证单个字段你的方法,
        然后加入到我们动态创建的Modelform类里面
        '''
        if readonly_fileds:
            for k,v in cls.base_fields.items():
                if hasattr(models_obj, "model"):
                    k_obj=models_obj.model._meta.get_field(k)
                else:
                    k_obj=models_obj._meta.get_field(k)
                if type(k_obj).__name__ in ('DateField','DateTimeField'):

                    v.widget.attrs['date']='datetimePicker'

                if k in readonly_fileds:

                    v.widget.attrs["class"] = "form-control custom-disabled"
                    v.widget.attrs["disabled"] = "true"
                elif k == 'teachers':
                    v.widget.attrs["class"] = "form-control custom-disabled"
                    v.queryset = models.UserProfile.objects.filter(role__name='老师')
                elif k == 'consultant':
                    v.widget.attrs["class"] = "form-control custom-disabled"
                    v.queryset = models.UserProfile.objects.filter(role__name='销售')

                else:
                    v.widget.attrs["class"] = "form-control"
        else:
            for k, v in cls.base_fields.items():
                if hasattr(models_obj, "model"):
                    k_obj = models_obj.model._meta.get_field(k)
                else:
                    k_obj = models_obj._meta.get_field(k)
                if type(k_obj).__name__ in ('DateField', 'DateTimeField'):
                    v.widget.attrs["date"] = 'datetimePicker'
                if k == 'teachers':
                    v.widget.attrs["class"] = "form-control custom-disabled"
                    v.queryset = models.UserProfile.objects.filter(role__name='老师')
                elif k == 'consultant':
                    v.widget.attrs["class"] = "form-control custom-disabled"
                    v.queryset = models.UserProfile.objects.filter(role__name='销售')
                else:
                    v.widget.attrs["class"]="form-control"



            if hasattr(models_obj,"clean_%s"%k):
                clean_field_func=getattr(models_obj,"clean_%s"%k)
                setattr(cls,"clean_%s"%k,clean_field_func)
        return forms.ModelForm.__new__(cls)#返回自己的__new__方法.
    def default_clean(self):
        '''给所有的forms加一个验证
        重写了clean方法
        开始设计这个方法的目的就是为了验证前段不可读字段是否被而已篡改
        思路:
        后端发回来的值需要经过modelform验证
        传过来的值再cleanned_data里面已经处理过一次
        我们需要再次验证就写了这个方法,加入到了ModelsForm里面
        instance 就是后台的该models下的某个对象的所以值
        cleanned_data 是前段穿过来 经过models里面定义规则验证后的值.



        '''
        self.ValidationError = ValidationError
        errot_list = []
        if getattr(models_obj,'readonly_table',None):
            raise self.ValidationError("当前表只读,不允许被修改或添加")
        if self.instance.id:#这不是是添加页面
            for read_only_field in readonly_fileds:
                ro_field_onfountend = self.cleaned_data.get(read_only_field)
                ro_field_ondb=getattr(self.instance,read_only_field)
                if hasattr(ro_field_ondb,'select_related'):
                    ro_field_ondb=set(ro_field_ondb.select_related())
                    ro_field_onfountend=set(ro_field_onfountend)




                if ro_field_ondb !=ro_field_onfountend:
                    self.add_error(read_only_field,'不允许被修改')


            if hasattr(models_obj,'default_form_validation'):
                response=models_obj.default_form_validation(self)
                if response:
                    errot_list.append(response)

            if errot_list:
                raise ValidationError(errot_list)




    if hasattr(models_obj,"model"):

        class Meta:
            model=models_obj.model
            fields="__all__"


    else:

        class Meta:
            model=models_obj
            fields="__all__"
    attr={"Meta":Meta}
    Forms_class=type("Forms_class",(forms.ModelForm,),attr)#通过type 动态创建出Modleform类
    setattr(Forms_class,"__new__",__new__)
    setattr(Forms_class,"clean",default_clean)#重写了clean方法
    return Forms_class

