from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    """
    扩展用户，需要在settings设置认证model
    """
    name = models.CharField(max_length=30, blank=True, null=True, verbose_name='姓名', help_text='姓名')
    birthday = models.DateField(null=True, blank=True, verbose_name='出生年月', help_text='出生年月')
    mobile = models.CharField(max_length=11, blank=True, null=True, verbose_name='电话', help_text='电话')
    gender = models.CharField(max_length=6, choices=(('male', '男'), ('female', '女')), default='male', verbose_name='性别', help_text='性别')

    class Meta:
        verbose_name_plural = verbose_name = '用户'

    def __str__(self):
        # 要判断name是否有值，如果没有，则返回username，否则使用createsuperuser创建用户访问与用户关联的模型会报错，
        # 页面（A server error occurred. Please contact the administrator.）
        # 后台（UnicodeDecodeError: 'gbk' codec can't decode byte 0xa6 in position 9737: illegal multibyte sequence）
        if self.name:
            return self.name
        else:
            return self.username


class VerifyCode(models.Model):
    """
    短信验证码，可以保存在redis等中
    """
    code = models.CharField(max_length=20, verbose_name='验证码', help_text='验证码')
    mobile = models.CharField(max_length=11, verbose_name='电话', help_text='电话')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '短信验证码'

    def __str__(self):
        return self.code
