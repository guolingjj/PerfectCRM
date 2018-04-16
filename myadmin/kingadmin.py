"""模拟一个admin"""
r_data={}#返回给前段的数据类型
from crm import models
from django.shortcuts import render,HttpResponse,redirect
class Baseadmin(object):#自定义样式的基类
    list_display = ()
    list_filter = ()
    action=['delete_test']
    list_search=[]
    readonly_table=False
    readonly_fileds=[]
    extra_fileds={}#需要额外显示的字段
    def delete_test(self,req,*args):
        '''自定义action操作'''
        id_str=''
        for i in args[0]:
            id_str+=str(i.id)+"_"

        req.path+="%s/delete"%id_str.strip("_")
        return redirect(req.path)
    def default_form_validation(self):
        pass
        '''用户自定制验证方法 相当于 django from 的clean()'''

class CustomFollowUpAdmin(Baseadmin):
    list_display = ['customer','followup_times','itention','consultant','data']
    list_filter=("customer",'itention','data','consultant')
    readonly_table = True
class RoleAdmin(Baseadmin):
    list_display = ['name']
class UserprofielAdmin(Baseadmin):
    list_display = ['name']
    readonly_fileds=["password"]
    filter_horizontal = ["groups",'user_permissions']
class CustomerAdmin(Baseadmin):
    list_display = ['name','qq','phone',"source",'referral_from','data']
    list_filter = ['name','consult_course',"source",'referral_from',"tag","data",]
    list_search=['name','qq']
    filter_horizontal = ["tag"]
    extra_fileds = {"报名情况":"extra_fields_func",
                    '增加课程':"extra_addclass_func",

                    }#订制额外的字段

    def extra_fields_func(self, *args, **kwargs):
        customer_obj=args[1]
        if customer_obj.status==4:
            list_enroll=''
            for i in (customer_obj.payment_set.all()):
                if i.pay_status==2:
                    list_enroll+='%s;'%i.pay_course.name
            return '已完%s报名'%list_enroll
        else:
            return "<a href='/crm/customer/%s/enrollment'>未完成报名</a>" % args[1].id
    def extra_addclass_func(self, *args, **kwargs):
        customer_obj = args[1]
        if customer_obj.status == 4:
            return "<a href='/crm/customer/%s/enrollment'>加一门课程</a>"% args[1].id
        else:
            return ''

    # readonly_fileds=["qq",'consult_course',]
    # readonly_table=True

    def default_form_validation(self):

        content=self.cleaned_data.get("content",'')
        if len(content)<15:
            return self.ValidationError("content内容不能少于15")

    def clean_name(self):
        if not self.cleaned_data["name"]:
            self.add_error("name","不能为空")
        else:
            return self.cleaned_data["name"]
class CourseRecordAdmin(Baseadmin):
    list_display=['day_num','home_title','teachers','data']
    extra_fileds = {'应到人数':'extra_fields_func',
                    '签到': 'extra_fields_func',
                    '迟到':'extra_fields_func',
                    '缺勤': 'extra_fields_func',
                    '早退': 'extra_fields_func',
                    '请假': 'extra_fields_func',
                    '详情':'class_infor_func'
                    }
    def class_infor_func(self,*args,**kwargs):
        print("xxxx:",args)
        CourseRecord_obj=args[1]

        return "<a href='/myadmin/crm/studyrecord/%s'>详情</a>"%CourseRecord_obj.id
    def extra_fields_func(self,*args,**kwargs):
        print(args)
        req=args[0]
        row_obj=args[1]
        field_name=args[2]

        stu_list=''
        if field_name=='应到人数':
            return row_obj.clazz.enrollment_set.filter(customer__status=4).count()
        elif field_name == '签到':
            stu_obj_queryset = row_obj.studyrecord_set.filter(attendance=0).all()
            for stu_obj in stu_obj_queryset:
                stu_list += "%s;" % stu_obj.student.name
            return "<a class='moreinfor' href='javascrpt:void(0)'>%s</a>"%(stu_obj_queryset.count())+"<span style='display:none'>签到:%s<span>"%stu_list
        elif field_name == '迟到':
            stu_obj_queryset = row_obj.studyrecord_set.filter(attendance=1).all()
            for stu_obj in stu_obj_queryset:
                stu_list += "%s;" % stu_obj.customer.name
            return "<a class='moreinfor' href='javascrpt:void(0)'>%s</a>"%(stu_obj_queryset.count())+"<span style='display:none'>迟到:%s<span>"%stu_list
        elif field_name == '缺勤':
            stu_obj_queryset = row_obj.studyrecord_set.filter(attendance=2).all()
            for stu_obj in stu_obj_queryset:
                stu_list += "%s;" % stu_obj.student.customer.name
            return"<a class='moreinfor' href='javascrpt:void(0)'>%s</a>"%(stu_obj_queryset.count())+"<span style='display:none'>缺勤:%s<span>"%stu_list
        elif field_name == '早退':
            stu_obj_queryset = row_obj.studyrecord_set.filter(attendance=3).all()
            for stu_obj in stu_obj_queryset:
                stu_list += "%s;" % stu_obj.student.name
            return "<a class='moreinfor' href='javascrpt:void(0)'>%s</a>"%(stu_obj_queryset.count())+"<span style='display:none'>早退:%s<span>"%stu_list
        elif field_name == '请假':
            stu_obj_queryset = row_obj.studyrecord_set.filter(attendance=4).all()
            for stu_obj in stu_obj_queryset:
                stu_list += "%s;" % stu_obj.student.name
            return "<a class='moreinfor' href='javascrpt:void(0)'>%s</a>"%(stu_obj_queryset.count())+"<span style='display:none'>请假:%s<span>"%stu_list

    def initialize_courserecord(self,req,cr_model):
        '''批量生成学生学习记录'''
        if len(cr_model)>1:
            return HttpResponse("只能选择一个班级")
        create_obj_list = []
        for obj in cr_model[0].clazz.enrollment_set.all():

           create_obj_list.append(models.StudyRecord(
                student=obj.customer.userprofile_set.get(),
                course_record=cr_model[0],
            ))
        try:
            models.StudyRecord.objects.bulk_create(create_obj_list)
        except Exception as e:
            return HttpResponse("请查看是否有重复学习记录被添加")
        return redirect('/myadmin/crm/studyrecord/?course_record_exact=%s'%cr_model[0].id)

    action = ['initialize_courserecord',]
    initialize_courserecord.short_description = "批量生成学生上课记录"


class PaymentAdmin(Baseadmin):
    list_display = ['customer','pay_course','amount','consultant','pay_status','data']
    list_filter=['customer','pay_course','consultant','pay_status','data']
    extra_fileds={'应缴纳金额':'get_pay_func',
                  '成为学员':'create_student_func'
                  }
    def get_pay_func(self,*args,**kwargs):
        payment_obj=args[1]
        return '%s元'%payment_obj.pay_course.price
    def create_student_func(self,*args,**kwargs):
        payment_obj = args[1]
        if payment_obj.pay_status==2:
            if payment_obj.customer.status==4:
                return '已是学员'
            else:
                return "<a href='/crm/create_student/%s'>生成学生账户</a>"%payment_obj.customer.id
        else:
            return '未完成缴费'
class StudyRecodeAdmin(Baseadmin):
    list_display = ['student','course_record','attendance','score','data']
    list_filter = ['student','course_record','data']
    extra_fileds={'作业':'home_work_down'}
    def home_work_down(self,*args,**kwargs):
        import os
        from PerfectCRM import settings
        studyrecord_obj=args[1]
        if args[1].has_submit_homework:
            stuhomework_base_dir = '%s{sep}%s{sep}第%s节{sep}%s' % (settings.STU_HOMEWORK_DATA_URL,
                                                                  studyrecord_obj.course_record.clazz,
                                                                  studyrecord_obj.course_record.day_num,
                                                                  studyrecord_obj.student.name,#1
                                                                  )
            stuhomework_base_dir = stuhomework_base_dir.format(sep=os.sep)
            print('路径',stuhomework_base_dir)
            if os.path.exists(stuhomework_base_dir):

                return "<a href='/teacher/down_homework/%s'>作业下载</a>"%args[1].id
            else:
                return '作业不见了'
        else:
            return "未提交作业"

def register(models_obj,custom_display=None):#自定义register方法
    if models_obj._meta.app_label not in r_data:#通过models.数据库对象的方法区获取add的名字
        r_data[models_obj._meta.app_label]={}#如果app名字存在则放在这儿
    if custom_display:
        custom_display.model=models_obj#关联models对象
        r_data[models_obj._meta.app_label][models_obj._meta.model_name]=custom_display
    else:
        r_data[models_obj._meta.app_label][models_obj._meta.model_name] = models_obj

register(models.Customer,CustomerAdmin)
register(models.Role,RoleAdmin)
register(models.UserProfile,UserprofielAdmin)
register(models.StudyRecord,StudyRecodeAdmin)
register(models.CourseRecord,CourseRecordAdmin)
register(models.Tag)
register(models.Menu)
register(models.Contract)
register(models.Clazz)
register(models.CustomFollowUp,CustomFollowUpAdmin)
register(models.Payment,PaymentAdmin)
register(models.Course)
register(models.Enrollment)
register(models.Brach)


