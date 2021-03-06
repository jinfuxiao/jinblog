from django.db import models

from django.contrib.auth.hashers import make_password


class User(models.Model):
    nickname = models.CharField(max_length=32, unique=True, null=False, blank=False)
    password = models.CharField(max_length=32)
    head = models.ImageField()
    age = models.IntegerField()
    sex = models.IntegerField()
    pid = models.IntegerField()

    def save(self):
        if not self.password.startswith('pbkdf2_'):
            # make_password()是django自带的功能，把密码加密
            self.password = make_password(self.password)
        super().save()

    @property
    def permission(self):
        return Permission.objects.get(self.pid)


class Permission(models.Model):
    perm = models.IntegerField()
    name = models.CharField(max_length=64)

