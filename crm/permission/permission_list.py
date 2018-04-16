#权限列表:{权限名字:['url','method','必要参数,不限定值','必要参数限定值']}
from crm.permission import custom_perm_func
perm_dict={

    'crm.can_access_submit_homework':[
        "stu_submit_homework",#这里是url的name,其实也可以写成固定url和动态url,加上参数urltype判断
        "GET",
        [],
        {}

    ],

    'crm.can_add_customer':[
        'add_data',
        'GET',
        [],
        {},
        custom_perm_func.can_add_customer,
    ],
    'crm.can_add_user':[
        'add_data',
        'GET',
        [],
        {},
        custom_perm_func.can_add_user,
    ],

}