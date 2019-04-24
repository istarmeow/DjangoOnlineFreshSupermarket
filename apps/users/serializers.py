import re
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import VerifyCode

User = get_user_model()


class VerifyCodeSerializer(serializers.Serializer):
    """"
    不用ModelSerializer原因：发送验证码只需要提交手机号码
    """
    mobile = serializers.CharField(max_length=11, help_text='手机号码', label='手机号码')

    def validate_mobile(self, mobile):
        """
        验证手机号码
        :param mobile:
        :return:
        """
        # 是否已注册
        if User.objects.filter(mobile=mobile):
            raise serializers.ValidationError('用户已存在')

        # 正则验证手机号码
        regexp = "^[1][3,4,5,7,8][0-9]{9}$"
        if not re.match(regexp, mobile):
            raise serializers.ValidationError('手机号码不正确')

        # 验证发送频率
        one_minute_ago = now() - timedelta(hours=0, minutes=1, seconds=0)  # 获取一分钟以前的时间
        # print(one_minute_ago)
        if VerifyCode.objects.filter(add_time__gt=one_minute_ago, mobile=mobile):
            # 如果添加时间大于一分钟以前的时间，则在这一分钟内已经发过短信，不允许再次发送
            raise serializers.ValidationError('距离上次发送未超过60s')

        return mobile
