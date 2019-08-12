from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import UserFav


@receiver(post_save, sender=UserFav)
def userfav_post_save_handler(sender, instance=None, created=False, **kwargs):
    # 首次创建时收藏数+1
    if created:
        goods = instance.goods
        goods.fav_num += 1
        goods.save()


@receiver(pre_delete, sender=UserFav)
def userfav_pre_delete_handler(sender, instance, **kwargs):
    # 删除前发送信号
    goods = instance.goods
    # 商品收藏数-1
    goods.fav_num -= 1
    if goods.fav_num < 0:
        goods.fav_num = 0
    goods.save()