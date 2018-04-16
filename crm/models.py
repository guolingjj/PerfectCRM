from django.db import models
from django.contrib.auth.models import User#django自带的验证
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe


# Create your models here.
class Customer(models.Model):
    '''客户信息表'''
    name = models.CharField(max_length=32,default='',verbose_name='名字')
    qq = models.CharField(max_length=64,unique=True)
    phone=models.CharField(max_length=64,blank=True,null=True,verbose_name='手机号码')
    qq_name=models.CharField(max_length=64,blank=True,null=True,verbose_name='qq名字')
    source_choice=((0,'转介绍'),
                    (1,'qq群'),
                    (2,'官网'),
                    (3,'百度推广'),
                    (4,'51CTO'),
                    (5,'知乎'),
                    (6,'市场推广'),

                    )
    status_choices=((0,"未报名"),#初始状态
                    (1,"等待填写报名信息"),#销售拉到客户生成报名信息表
                    (2,"等待审核"),#学员填写好了报名信息,等待销售审核信息
                    (3,"等待缴费"),#销售审核完信息,等待缴费
                    (4,"学员"),#财务确认缴费

                    )
    status=models.SmallIntegerField(choices=status_choices,default=0,verbose_name='报名状态')
    source = models.SmallIntegerField(choices=source_choice,verbose_name='来源于')
    referral_from = models.CharField(verbose_name='转介紹人',max_length=64,blank=True)
    consult_course = models.ForeignKey('Course',verbose_name='咨询课程',on_delete=models.CASCADE)
    content = models.TextField(verbose_name="咨询详情")
    consultant=models.ForeignKey("UserProfile",on_delete=models.CASCADE,verbose_name='接待人')
    memo=models.TextField(null=True,blank=True,verbose_name='备注')
    tag=models.ManyToManyField('Tag',null=True,blank=True,verbose_name='标签')
    data=models.DateTimeField(auto_now_add=True,verbose_name='时间')
    id_num=models.CharField(max_length=64,null=True,blank=True,verbose_name="身份证")
    email=models.EmailField(max_length=64,null=True,blank=True,verbose_name="常用邮箱")
    def __str__(self):
        return self.name
    class Meta:
        verbose_name="客户表"

class Tag(models.Model):
    '''标签'''
    name=models.CharField(unique=True,max_length=32)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name="标签"

class CustomFollowUp(models.Model):
    '''客户跟进表'''
    customer=models.ForeignKey("Customer",on_delete=models.CASCADE,verbose_name='客户名')
    content=models.TextField(verbose_name="跟进内容")
    consultant=models.ForeignKey('UserProfile',on_delete=models.CASCADE,verbose_name='跟进人')
    itention_choice=((0,'2周内报名'),
                     (1,'一月内报名'),
                     (2,'无报名计划'),
                     (3,'已在其他机构报名'),
                     (4,'已报名'),
                     (5,'已拉黑'),
                     )
    followup_times=models.PositiveSmallIntegerField(verbose_name='跟进次数',default=1)
    itention=models.SmallIntegerField(choices=itention_choice,verbose_name='计划')
    data=models.DateTimeField(auto_now_add=True,verbose_name='时间')
    def __str__(self):
        return '客户:%s第%s次跟进'%(self.customer,self.followup_times)
    class Meta:
        verbose_name="客户跟进表"
        unique_together=('customer','followup_times')

class CourseRecord(models.Model):
    '''上课记录'''
    clazz=models.ForeignKey('Clazz',on_delete=models.CASCADE,verbose_name='班级')
    has_homework=models.BooleanField(default=True,verbose_name='是否有作业')
    home_title=models.CharField(max_length=32,verbose_name='作业的标题')
    outline=models.CharField(max_length=128,verbose_name="本节课的大纲")
    homework=models.TextField(null=True,blank=True,verbose_name='作业的内容')
    day_num=models.PositiveSmallIntegerField(verbose_name="第几节课")
    teachers=models.ForeignKey("UserProfile",on_delete=models.CASCADE,verbose_name='上课老师')
    data=models.DateField(auto_now_add=True,verbose_name='上课时间')
    def __str__(self):
        return '%s的第%s节课程记录'%(self.clazz,self.day_num)
    class Meta:
        unique_together=("clazz",'day_num')


        verbose_name = "上课记录"

class StudyRecord(models.Model):
    '''学习记录'''
    student=models.ForeignKey('UserProfile',on_delete=models.CASCADE,verbose_name='学生姓名')
    course_record=models.ForeignKey('CourseRecord',on_delete=models.CASCADE,verbose_name='上课记录')
    attendance_choice=((0,'已签到'),
                       (1,'迟到'),
                       (2,'缺勤'),
                       (3,'早退'),
                       (4,'请假'),
                       )
    attendance=models.PositiveSmallIntegerField(choices=attendance_choice,default=0,verbose_name='考勤')
    score_choice=((100,"A+"),
                  (90,"A"),
                  (80,"B"),
                  (60,"C"),
                  (40,"D"),
                  (-50,"E"),
                  (-100,"copy"),
                  (0,"N/A"),

                    )
    has_submit_homework=models.BooleanField(default=False,verbose_name='是否提交作业')
    score=models.SmallIntegerField(choices=score_choice,default=0,verbose_name='成绩')
    memo=models.TextField(blank=True,null=True,verbose_name='本节课备注')
    data=models.DateTimeField(auto_now_add=True,verbose_name='学习时间')
    def __str__(self):
        return "学生%s的%s"%(self.student,self.course_record,)

    class Meta:
        verbose_name="学习记录"
        unique_together=('student','course_record')

class Course(models.Model):
    '''课程表'''
    name=models.CharField(max_length=64,unique=True,verbose_name='课程名字')
    price=models.PositiveSmallIntegerField(verbose_name='课程价格')
    period=models.PositiveSmallIntegerField(verbose_name="课程周期")

    outline = models.TextField(verbose_name='课程大纲')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name="课程表"

class Brach(models.Model):
    '''校区'''
    name=models.CharField(max_length=64,unique=True)
    addr=models.CharField(max_length=128)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name="校区"

class Clazz(models.Model):
    '''班级表'''
    brach=models.ForeignKey("Brach",on_delete=models.CASCADE,verbose_name='校区')
    contract=models.ForeignKey("Contract",on_delete=models.CASCADE,verbose_name="合同")
    course=models.ForeignKey("Course",on_delete=models.CASCADE,verbose_name='课程名字')
    semester=models.PositiveSmallIntegerField(verbose_name='学期')
    teachers=models.ManyToManyField('UserProfile',verbose_name='班级老师')
    type_choice=((0,'面授(脱产)'),
                 (1,"面授(周末)"),
                 (2,"面授(全期)"),
                 (3,"网络"),
                 )
    type=models.SmallIntegerField(choices=type_choice)
    start_data=models.DateField(verbose_name='开班日期')
    end_data=models.DateField(verbose_name='结业日期',blank=True,null=True)

    def __str__(self):
        return "%s-%s课程-%s期"%(self.brach,self.course,self.semester)
    class Meta:
        unique_together=("brach",'course','semester')
        verbose_name="班级"

class Enrollment(models.Model):

    '''报名表'''
    customer=models.ForeignKey('Customer',on_delete=models.CASCADE,verbose_name='客户')
    enrolled_clazz=models.ForeignKey('clazz',verbose_name='所报班级',on_delete=models.CASCADE)
    consultant=models.ForeignKey('UserProfile',verbose_name="签单人",on_delete=models.CASCADE)
    contract_agreed=models.BooleanField(default=False,verbose_name="学员同意")
    consultant_approval=models.BooleanField(default=False,verbose_name="审核人已审核")
    data=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return '客户%s的%s课程报名表'%(self.customer,self.enrolled_clazz)
    class Meta:
        unique_together=('customer','enrolled_clazz')


        verbose_name = "报名表"

class Payment(models.Model):
    '''缴费表'''
    customer=models.ForeignKey('Customer',on_delete=models.CASCADE)
    pay_course=models.ForeignKey("Course",verbose_name='缴费课程',on_delete=models.CASCADE)
    amount=models.PositiveIntegerField(verbose_name="已交数额",default=500)
    consultant=models.ForeignKey('UserProfile',verbose_name="协助缴费人",on_delete=models.CASCADE)
    data=models.DateTimeField(auto_now_add=True)
    pay_status_choice=((0,'未缴费'),
                       (1,"已缴纳部分金额"),
                       (2,"已缴费"),
                       )
    pay_status=models.SmallIntegerField(choices=pay_status_choice,default=0)
    def __str__(self):
        return "<%s %s>"%(self.customer,self.pay_course)
    class Meta:
        unique_together=('customer','pay_course')
        verbose_name="缴费记录"

class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, stu_customer=None, password=None, ):
        """
        Creates and saves a User with the given email,  and password.
        """
        if not email:
            raise ValueError('Users must have an email addres')

        user = self.model(
            email=self.normalize_email(email),
            name=name,

            stu_customer=stu_customer,
        )

        user.set_password(password)

        self.is_active=True
        user.save(using=self._db)
        return user

    def create_superuser(self, email,name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='邮箱',
        max_length=255,
        unique=True,

    )
    password = models.CharField(_('password'), max_length=128,help_text=mark_safe("<a href='../password_reset'>点我改密码</a>"))
    name=models.CharField(max_length=32,verbose_name='用户姓名')
    stu_customer=models.OneToOneField("Customer",null=True,blank=True,verbose_name='用户对应的客户',on_delete=models.CASCADE,help_text='只有交费成功的用户能够注册')
    role=models.ManyToManyField("Role",verbose_name='角色')
    is_active = models.BooleanField(default=True,verbose_name='是否活跃')
    is_admin = models.BooleanField(default=False,verbose_name='是否是管理员')
    objects = UserProfileManager()
    USERNAME_FIELD = 'email'#以xx字段为用户名
    REQUIRED_FIELDS = ['name','role']#那些字段是必须

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    class Meta:
        verbose_name="用户"
        permissions=(("can_access_submit_homework","可以提交作业"),
                     ('can_add_customer','可以添加客户'),
                     ('can_add_user','可以添加用户')
                     )

class Contract(models.Model):
    name=models.CharField(max_length=32,verbose_name='名字')
    content=models.CharField(max_length=1024,verbose_name='合同')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name="合同"

class Role(models.Model):
    '''角色表'''
    name=models.CharField(max_length=32,verbose_name='角色名字')
    menus=models.ManyToManyField("Menu",blank=True,verbose_name='角色菜单')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name="角色"

class Menu(models.Model):
    name=models.CharField(max_length=32,verbose_name='菜单名字')
    url_name=models.CharField(max_length=128,verbose_name='菜单url')
    url_type_choices = ((0, "alias"), (1, "absolute_url"))
    url_type = models.SmallIntegerField(choices=url_type_choices, default=0,verbose_name='菜单类型')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name="菜单"
