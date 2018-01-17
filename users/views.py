from django.shortcuts import render
from users.forms import RegisterForm, LoginForm
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 一般session保存比较小的东西
            request.session['uid'] = user.id

    return render(request, 'register.html', {})

def login(request):
    return render(request, 'login.html', {})
