# coding:utf-8
from django.shortcuts import render
from users.models import Permission


def check_permission(user, perm_name):
    user_perm = Permission.objects.get(id=user.pid)
    need_perm = Permission.objects.get(name=perm_name)
    # 比较perm的大小，返回布尔值
    return user_perm.perm >= need_perm.perm


def permit(perm_name):
    def wrap1(view_func):
        def wrap2(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if not user:
                if check_permission(user, perm_name):
                    return view_func(request, *args, **kwargs)
            return render(request, 'block.html')
        return wrap2
    return wrap1

# 权限管理根据传入的perm不同，判断是否执行view_func或者跳转到登录、注册状态
# 用管理员权限为例，perm的id是3，描述是能修改文章本身
# def permit(perm):
#     def wrap1(view_func):
#         def wrap2(request, *args, **kwargs):
#             # 首先通过request去获取user不能获取到，是最低权限
#             # user = request.user这样即使没有也不会报错
#             # 没有的话返回None
#             # 类似的hasattr, setattr--内建函数
#             user = getattr(request, 'user', None)
#             if not user:
#                 return '提示权限不够'
#             else:
#             # 登录的话执行判断，是普通用户还是管理员？
#                 aid = user[id]
#                 pid = User.objests.get(id=aid).only('pid')
#                 # 通过aid 获取 pid
#                 # 判断pid == perm 的id
#                 if pid == Permission.objects.get(name=perm).only('id'):
#                     response = view_func(request, *args, **kwargs)
#                     return response
#                 else:
#                     return '提示权限不够'
#         return wrap2
#     return wrap1