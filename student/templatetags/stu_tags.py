from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import timedelta, datetime
from myadmin.utils import paginator
from django.db.models import Avg,Max,Min,Sum
register = template.Library()


@register.simple_tag
def handle_score(enroll_obj):
    #防止老师填错,所以加上学习记录中的班级id与报名信息中的id相等
    # print(enrollment.studyrecord_set.all())


    return enroll_obj.customer.userprofile.studyrecord_set.filter(course_record__clazz_id=enroll_obj.enrolled_clazz.id)\
    .aggregate(Sum("score"))["score__sum"]#报名表对应的学生学习记录里的班级id=该报名所报班级id.







