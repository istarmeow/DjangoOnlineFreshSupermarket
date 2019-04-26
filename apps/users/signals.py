from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user(sender, instance=None, created=False, **kwargs):
    if created:
        password = instance.password  # instance指的就是创建的用户对象
        instance.set_password(password)
        instance.save()
