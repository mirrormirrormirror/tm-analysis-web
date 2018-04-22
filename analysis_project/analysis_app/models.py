from django.db import models
from retry import retry

# Create your models here.


class user(models.Model):
    # book = models.ManyToManyField(book)
    user_num = models.CharField("用户帐号", max_length=100)
    user_pw = models.CharField("密码", max_length=100)
    user_name = models.CharField("用户名", max_length=30, null=True)
    user_sex = models.BooleanField("性别", max_length=1, choices=((0, "男"), (1, "女")), default=0)
    user_email = models.EmailField("邮箱", null=True)

