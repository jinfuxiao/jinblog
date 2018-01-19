from django.shortcuts import render, redirect
from users.forms import RegisterForm, LoginForm
# Create your views here.

def register(request):
    # 对于表单提交
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # 对user做其他修改
            user.save()
            # 一般session保存比较小的东西,主要是关于用户状态的东西
            request.session['uid'] = user.id
            return redirect('/user/info/?')
        else:
            return render(request, 'register.html', {'errors': form.errors})

    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user, passed = form.chk_password()
            if passed:
                # 用session记录维持识别是否登录，和用哪种方式进行登录注册没有关系
                request.session['uid'] = user.id
                return redirect('/user/info')
        else:
            return render(request, 'login.html', {'errors': form.errors})
    return render(request, 'login.html')

# @login_required，登陆后查看详细信息这个装饰器，我们用中间件实现
def info(request):
    return render(request, 'info.html', {'user': request.user})


def logout(request):
    # del request.session['uid']
    request.session.flush()
    return redirect('/post/home/')



