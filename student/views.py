from django.shortcuts import render,HttpResponse
from django.db.models import Avg,Max,Min,Sum
from crm import models
from django.http import FileResponse
import os
from PerfectCRM import settings
from django.contrib.auth.decorators import login_required
from crm.permission.permission_handle import check_permission

# Create your views here.
@login_required
def home_work_url(req,studyrecord_obj):
    '''获取学生作业路径'''

    stuhomework_base_dir = '%s{sep}%s{sep}第%s节{sep}%s' % (settings.STU_HOMEWORK_DATA_URL,
                                              studyrecord_obj.course_record.clazz,
                                              studyrecord_obj.course_record.day_num,
                                              req.user.name,
                                              )
    stuhomework_base_dir=stuhomework_base_dir.format(sep=os.sep)

    if os.path.exists(stuhomework_base_dir):
        return (stuhomework_base_dir,True)
    else:
        return (stuhomework_base_dir,False )
@login_required
def student_index(req):

    enrollments=req.user.stu_customer.enrollment_set.all()

    return render(req,'student/stu_index.html',{'enrollments':enrollments})
@login_required
def course_record(req,enrollment_id):


    # enrollment = req.user.stu_customer.enrollment_set.get(id=enrollment_id)


    return render(req, 'student/class_record.html', )
# @check_permission
@login_required
def stu_submit_homework(req,studyrecord_id):

    studyrecord_obj=models.StudyRecord.objects.get(id=studyrecord_id)
    homework_names = []
    if req.is_ajax():
        # base/班级/第几节/学生/xx.zip

        if not home_work_url(req,studyrecord_obj)[1]:

            os.makedirs(home_work_url(req,studyrecord_obj)[0], exist_ok=True)
            for k,v in req.FILES.items():
                with open('%s/%s'%(home_work_url(req,studyrecord_obj)[0],v.name),'wb') as f:
                    for chunk in v.chunks():
                        f.write(chunk)

            studyrecord_obj.has_submit_homework = True
            studyrecord_obj.save()


    elif req.method=="GET":
        if home_work_url(req,studyrecord_obj)[1]:
            homework_names=os.listdir(r'%s'%home_work_url(req,studyrecord_obj)[0])

    return render(req,"student/homework.html",{'studyrecord_obj':studyrecord_obj,"homework_names":homework_names,})

@login_required
def hm_file_down(request,studyrecord_id,name):

    studyrecord_obj = models.StudyRecord.objects.get(id=studyrecord_id)
    home_work_url(request, studyrecord_obj)[0]


    file=open(home_work_url(request, studyrecord_obj)[0]+os.sep+name,'rb')
    response =FileResponse(file)
    response['Content-Type']='application/octet-stream'
    response['Content-Disposition']='attachment;filename="%s"'%name
    return response