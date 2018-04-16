# 处理权限
from django.urls import resolve
from PerfectCRM import settings
from django.shortcuts import render, HttpResponse, redirect
from crm.permission.permission_list import perm_dict
from crm.permission import custom_perm_func


def perm_check(*args, **kwargs):
    req = args[0]  # 获取到view函数中的req请求
    resolve_url_obj = resolve(req.path)
    cur_url_name = resolve_url_obj.url_name
    user_perm_list = req.user.get_all_permissions()
    kwargs_match = False
    args_match = False
    url_match = False
    method_metch = False
    customer_perm = False
    custom_perm_func = None
    # 判断用户是否认证
    if not req.user.is_authenticated:
        print("this.....")
        return redirect(settings.LOGIN_URL)

    print(user_perm_list)

    for user_perm in user_perm_list:
        if perm_dict.get(user_perm):  # 判断该权限是不是在自定义权限当中
            perm_val = perm_dict[user_perm]

            per_url_name = perm_val[0]  # 必有的值

            per_method = perm_val[1]  # 必有的值
            perm_args = perm_val[2]  # 可能没有
            perm_kwargs = perm_val[3]  # 可能没有
            custom_perm_func = None if len(perm_val) == 4 else perm_val[4]
            print('custom_perm_func', custom_perm_func)

            if cur_url_name == per_url_name:  # 验证url是否正确
                url_match = True
                if per_method == req.method:  # 验证请求方式是否正确
                    method_metch = True
                    method_func = getattr(req, req.method)  # req.GET or req.POST
                    # 验证参数是否正确
                    if not perm_args:
                        args_match = True
                    else:
                        for iterm_arg in perm_val[2]:
                            if method_func.get(iterm_arg, None):
                                args_match = True

                            else:
                                args_match = False
                                break  # 匹配失败直接跳出
                    # 验证参数的值是否正确
                    if not perm_kwargs:
                        kwargs_match = True
                    for k, v in perm_val[3].items():
                        if method_func.get(k, None) == v:
                            kwargs_match = True
                        else:
                            kwargs_match = False
                            break
                else:
                    method_metch=False



            else:
                url_match=False



                # 自定义权限验证
            print('11111',customer_perm)
            if custom_perm_func:
                print(user_perm,'有自定义函数')

                if custom_perm_func(req, args, kwargs):
                    print('自定义权限钩子返回值',custom_perm_func(req, args, kwargs))
                    customer_perm = True
                else:
                    customer_perm=False


            else:
                print('没有自定义函数')
                customer_perm = True

        match_all = [url_match, method_metch, kwargs_match, args_match, customer_perm]

        if all(match_all):
            print("--------------------------------------okok 你有权限 ")
            print(match_all)
            return True
        else:
            print("---------------------------------------当前用户无此权限")
            print(match_all)
    return False


def check_permission(func):
    def inner(*args, **kwargs):
        if not perm_check(*args, **kwargs):
            request = args[0]
            return HttpResponse("您没有该操作权限")
        print('args', args)
        print('kwargs', kwargs)
        return func(*args, **kwargs)

    return inner
