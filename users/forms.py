from django.forms import ModelForm, Form
from users.models import User

class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'password', 'avatar', 'age', 'sex']


class LoginForm(Form):
    pass

