from django import template


register = template.Library()



@register.simple_tag
def get_filter_stu_num(courserecord_obj,attendance):





    return courserecord_obj.studyrecord_set.filter(attendance=attendance).count()
@register.simple_tag
def get_filter_stu_list(courserecord_obj,attendance):
    stu_list=''
    stu_obj_queryset = courserecord_obj.studyrecord_set.filter(attendance=attendance).all()
    for stu_obj in stu_obj_queryset:
        stu_list+="%s;"%stu_obj.student.customer.name
    return stu_list
