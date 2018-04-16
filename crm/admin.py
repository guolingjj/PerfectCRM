from django.contrib import admin
from crm import models
from django.shortcuts import render,HttpResponse,redirect
# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('qq','name','source',"data")
    list_filter = ('source',"data","name")
    list_per_page = 4
    search_fields = ("name","qq")
    filter_horizontal = ["tag"]
    actions = ["test"]
    # readonly_fields = ["qq"]
    def test(self,req,*args):
        print("xxx:",req)
        print("yyy:",args)
        return HttpResponse("ok")

    #ordering =

class ClazzAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        print('1111',db_field)
        print('2222',request)
        print('3333',kwargs)
        kwargs["queryset"] = models.UserProfile.objects.filter(role__name='老师')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','name')



#-------------------------------------------copy
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from crm.models import UserProfile as MyUser

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format

        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'name', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_admin','stu_customer')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_admin',"is_active",'groups','user_permissions','role','stu_customer'),}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ("groups",'user_permissions')

class CourseRecordAdmin(admin.ModelAdmin):
    def initialize_courserecord(self,req,cr_model):
        '''批量生成学生学习记录'''
        if len(cr_model)>1:
            return HttpResponse("只能选择一个班级")
        create_obj_list = []
        for obj in cr_model[0].clazz.enrollment_set.all():
            # models.StudyRecord.objects.get_or_create(**{
            #     'student':obj,
            #     "course_record":cr_model[0]
            # })

            create_obj_list.append(models.StudyRecord(
                student=obj,
                course_record=cr_model[0],
            ))
        try:
            models.StudyRecord.objects.bulk_create(create_obj_list)
        except Exception as e:
            return HttpResponse("请查看是否有重复学习记录被添加")
        return redirect('/admin/crm/studyrecord/?course_record__id__exact=%s'%cr_model[0].id)

    actions = ['initialize_courserecord',]
    initialize_courserecord.short_description = "批量生成学生上课记录"

class StudyRecodeAdmin(admin.ModelAdmin):
    list_display = ['student','course_record','attendance','score','data']
    list_filter = ['student','course_record','data']

# Now register the new UserAdmin...
admin.site.register(MyUser, UserProfileAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
admin.site.register(models.Customer,CustomerAdmin)
# admin.site.register(models.UserProfile)
admin.site.register(models.Enrollment)
admin.site.register(models.Course)
admin.site.register(models.Clazz,ClazzAdmin)

admin.site.register(models.Brach)
admin.site.register(models.CourseRecord,CourseRecordAdmin)
admin.site.register(models.CustomFollowUp)
admin.site.register(models.Payment)
admin.site.register(models.Role)
admin.site.register(models.StudyRecord,StudyRecodeAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Menu)
admin.site.register(models.Contract)