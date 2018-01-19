# coding: utf-8

from django.shortcuts import redirect, render
from django.utils.deprecation import MiddlewareMixin
from users.models import User

class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path in ['/user/register/', '/user/login/']:
            return
        else:
            uid = request.session.get('uid')
            if uid is not None:
                user = User.objects.get(id=uid)
                request.user = user
            else:
                # /user/login/ 最前面的必须加/
                return redirect('/user/login/')

