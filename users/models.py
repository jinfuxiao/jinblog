from django.db import models

from django.contrib.auth.hashers import make_password
# Create your models here.

class User(models.Model):
    nickname = models.CharField(max_length=32, unique=True, null=False, blank=False)
    # email = models.EmailField(max_length=126)
    password = models.CharField(max_length=32)
    avatar = models.ImageField()
    age = models.IntegerField()
    sex = models.IntegerField()

