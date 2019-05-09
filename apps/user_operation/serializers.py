from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import UserFav


class UserFavSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()  # 表示user为隐藏字段，默认为获取当前登录用户
    )

    class Meta:
        model = UserFav
        fields = ['user', 'goods', 'id']
        # UserFav项目属于父列表，并且有一个由“position”字段定义的顺序。给定列表中的任何两项不得共享同一位置。
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message='已经收藏'
            )
        ]
