from django.db import models
from goods.models import Goods
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFav(models.Model):
    """
    用户收藏
    """
    user = models.ForeignKey(User, verbose_name='用户', help_text='用户', on_delete=models.CASCADE, related_name='favs')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品', help_text='商品', related_name='favs')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '用户收藏'
        unique_together = ['user', 'goods']

    def __str__(self):
        return "{} 收藏 {}".format(self.user.name if self.user.name else self.user.username, self.goods.name)


class UserLeavingMessage(models.Model):
    """
    用户留言
    """
    MESSAGE_TYPE = (
        (1, '留言'),
        (2, '投诉'),
        (3, '询问'),
        (4, '售后'),
        (5, '求购')
    )
    user = models.ForeignKey(User, verbose_name='用户', help_text='用户', on_delete=models.CASCADE, related_name='leaving_msgs')
    message_type = models.IntegerField(default=1, choices=MESSAGE_TYPE, verbose_name='留言类型', help_text='留言类型：1-留言，2-投诉， 3-询问， 4-售后， 5-求购')
    subject = models.CharField(max_length=100, default='', verbose_name='主题', help_text='主题')
    message = models.TextField(default='', verbose_name='留言内容', help_text='留言内容')
    file = models.FileField(upload_to='upload/leaving_msg/', blank=True, null=True, verbose_name='上传文件', help_text='上传文件')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '用户留言'

    def __str__(self):
        return '{} {}:{}'.format(self.user.name if self.user.name else self.user.username, self.get_message_type_display(), self.subject)


class UserAddress(models.Model):
    """
    用户收货地址
    """
    user = models.ForeignKey(User, verbose_name='用户', help_text='用户', on_delete=models.CASCADE, related_name='addresses')
    province = models.CharField(max_length=100, default='', verbose_name='省份', help_text='省份')
    city = models.CharField(max_length=100, default='', verbose_name='城市', help_text='城市')
    district = models.CharField(max_length=100, default='', verbose_name='区域', help_text='区域')
    address = models.CharField(max_length=200, default='', verbose_name='收货地址', help_text='收货地址')
    signer_name = models.CharField(max_length=20, default='', verbose_name='签收人', help_text='签收人')
    signer_mobile = models.CharField(max_length=11, verbose_name='联系电话', help_text='联系电话')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '收货地址'

    def __str__(self):
        return self.address

