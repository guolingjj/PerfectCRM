from django.shortcuts import render,HttpResponse,redirect
from crm import models
from teacher import forms
from django.db.utils import IntegrityError

# Create your views here.
def teacher_index(req):
    class_obj_queryset=models.Clazz.objects.filter(teachers=req.user.id).all()
    print(class_obj_queryset)
    return render(req,'teacher/teacher_index.html',{'class_obj_queryset':class_obj_queryset})
def teacher_courserecord(req,class_id):
    courserecord_obj_queryset=models.CourseRecord.objects.filter(clazz=class_id).all()

    print(courserecord_obj_queryset)
    return render(req,'teacher/teacher_courserecord.html',{'courserecord_obj_queryset':courserecord_obj_queryset})

def teacher_courserecord_add(req,class_id):
    clazz_obj=models.Clazz.objects.get(id=class_id)
    error=''
    if req.method=="GET":
        RCforms=forms.Courserecordtmodelform()
        return render(req,'teacher/teacher_courserecord_add.html',{'clazz_obj':clazz_obj,'RCforms':RCforms,'error':error})
    elif req.method=="POST":

        print(req.POST)
        # second_dict=dict(req.POST)
        # second_dict['clazz']=class_id
        # second_dict['teachers']=req.user.id
        # second_dict['day_num']=1
        # print(second_dict)
        RCforms = forms.Courserecordtmodelform(req.POST)
        if RCforms.is_valid():
            RCforms.cleaned_data['clazz']=models.Clazz.objects.get(id=class_id)
            RCforms.cleaned_data['teachers']=models.UserProfile.objects.get(id=req.user.id)
            try:
                models.CourseRecord.objects.create(**RCforms.cleaned_data)
            except IntegrityError as e:
                error='添加课程天数已存在'
                return render(req, 'teacher/teacher_courserecord_add.html', {'clazz_obj':clazz_obj,'RCforms': RCforms, 'error': error})

            return redirect(req.path.replace('add',''))
        else:
            error=RCforms.errors
            return render(req, 'teacher/teacher_courserecord_add.html', {'clazz_obj':clazz_obj,'RCforms': RCforms, 'error': error})

def down_homework(req,stu_record_id):
    import os
    from PerfectCRM import settings
    from django.http import FileResponse
    studyrecord_obj = models.StudyRecord.objects.get(id=stu_record_id)
    stuhomework_base_dir = '%s{sep}%s{sep}第%s节{sep}%s' % (settings.STU_HOMEWORK_DATA_URL,
                                                          studyrecord_obj.course_record.clazz,
                                                          studyrecord_obj.course_record.day_num,
                                                          studyrecord_obj.student.name,
                                                          )
    stuhomework_base_dir = stuhomework_base_dir.format(sep=os.sep)
    name=os.listdir(stuhomework_base_dir)[0]
    file = open(stuhomework_base_dir + os.sep + name, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="%s"' % name
    return response