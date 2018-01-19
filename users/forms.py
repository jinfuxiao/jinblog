from django.forms import ModelForm, Form, CharField
from django.contrib.auth.hashers import check_password
from users.models import User

class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'password', 'head', 'age', 'sex']


class LoginForm(Form):
    nickname = CharField(max_length=64)
    password = CharField(max_length=32)

    def chk_password(self):
        # cleaned_data,页面提交上来的是字符串，django的表单会处理成我们需要的数据类型
        nickname = self.cleaned_data['nickname']
        password = self.cleaned_data['password']
        try:
            user = User.objects.get(nickname=nickname)
            return check_password(password, user.password)
        except:
            return None, False





