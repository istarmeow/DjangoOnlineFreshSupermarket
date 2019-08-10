from django.db import models
from goods.models import Goods
# from users.models import UserProfile  # 但是某些情况下我们不知道用户的模型，可以直接使用下方的方法获取用户model
from django.contrib.auth import get_user_model

User = get_user_model()


class ShoppingCart(models.Model):
    """
    购物车
    """
    user = models.ForeignKey(User, verbose_name='用户', help_text='用户', on_delete=models.CASCADE, related_name='shopping_carts')
    goods = models.ForeignKey(Goods, verbose_name='商品', help_text='商品', on_delete=models.CASCADE)
    nums = models.IntegerField(default=0, verbose_name='购买数量', help_text='购买数量')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '购物车'
        unique_together = ['user', 'goods']  # 用户和商品联合唯一

    def __str__(self):
        return "{}({})".format(self.goods.name, self.nums)


class OrderInfo(models.Model):
    """
    订单
    """
    # ORDER_STATUS = (
    #     ('success', '成功'),
    #     ('cancel', '取消'),
    #     ('topaid', '待支付')
    # )
    ORDER_STATUS = (
        ('TRADE_FINISHED', '交易完成'),
        ('TRADE_SUCCESS', '支付成功'),
        ('WAIT_BUYER_PAY', '交易创建'),
        ('TRADE_CLOSE', '交易关闭')
    )
    user = models.ForeignKey(User, verbose_name='用户', help_text='用户', on_delete=models.CASCADE, related_name='order_infos')
    order_sn = models.CharField(max_length=30, unique=True, blank=True, null=True, verbose_name='订单号', help_text='订单号')
    trade_no = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付交易号', help_text='支付交易号')
    pay_status = models.CharField(choices=ORDER_STATUS, default='WAIT_BUYER_PAY', max_length=20, verbose_name='订单状态', help_text='订单状态')
    post_script = models.CharField(max_length=50, blank=True, null=True, verbose_name='订单留言', help_text='订单留言')
    order_amount = models.FloatField(default=0.0, verbose_name='订单金额', help_text='订单金额')
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name='支付时间', help_text='支付时间')
    # 用户信息
    address = models.CharField(max_length=200, default='', verbose_name='收货地址', help_text='收货地址')
    signer_name = models.CharField(max_length=20, default='', verbose_name='签收人', help_text='签收人')
    signer_mobile = models.CharField(max_length=11, verbose_name='联系电话', help_text='联系电话')

    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '订单'
        ordering = ['-add_time']

    def __str__(self):
        return "{}".format(self.order_sn)


class OrderGoods(models.Model):
    """
    订单商品详情
    """
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name='订单信息', help_text='订单信息', related_name='order_goods')
    goods = models.ForeignKey(Goods, verbose_name='商品', help_text='商品', blank=True, null=True, on_delete=models.SET_NULL)
    goods_nums = models.IntegerField(default=0, verbose_name='购买数量', help_text='购买数量')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '订单商品'

    def __str__(self):
        return str(self.order.order_sn)
