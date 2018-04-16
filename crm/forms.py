from django.forms import ModelForm
from django import forms
from crm import models

class Enrollmentmodelform(ModelForm):
    def __new__(cls,*args,**kwargs):


        for k,v in cls.base_fields.items():
            v.widget.attrs["class"] = "form-control "


        return forms.ModelForm.__new__(cls)#返回自己的__new__方法.
    class Meta:
        model=models.Enrollment
        fields=['enrolled_clazz','consultant']

class Customerform(ModelForm):
    def __new__(cls,*args,**kwargs):


        for k,v in cls.base_fields.items():
            if k in cls.Meta.readonly_fields:
                v.widget.attrs["class"] = "form-control disabled_field"
                v.widget.attrs["disabled"] = "disabled"
            else:
                v.widget.attrs["class"] = "form-control "


        return forms.ModelForm.__new__(cls)

    def clean_qq(self):
        if self.instance.qq!=self.cleaned_data['qq']:
            self.add_error("qq",'请不要修改不可变动字段')
        else:
            return self.cleaned_data['qq']
    def clean_consult_course(self):
        if self.instance.consult_course!=self.cleaned_data['consult_course']:
            self.add_error("consult_course",'请不要修改不可变动字段')
        else:
            return self.cleaned_data['consult_course']
    def clean_consultant(self):
        if self.instance.consultant!=self.cleaned_data['consultant']:
            self.add_error("consultant",'请不要修改不可变动字段')
        else:
            return self.cleaned_data['consultant']
    class Meta:
        model=models.Customer
        fields="__all__"
        exclude=['status','tag',"source",'memo','content','referral_from']
        readonly_fields=['consult_course','qq','consultant']