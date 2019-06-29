from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q
from random import choice
from django.contrib.auth.backends import ModelBackend
from rest_framework import mixins, viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import VerifyCodeSerializer, UserSerializer, UserDetailSerializer
from utils.user_op import send_sms
from .models import VerifyCode

User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户登录，可以使用用户名和手机登录，重写authenticate方法
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SendSmsCodeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = VerifyCodeSerializer

    def generate_code(self):
        # 定义一个种子，从这里面随机拿出一个值，可以是字母
        seeds = "1234567890"
        # 定义一个空列表，每次循环，将拿到的值，加入列表
        random_str = []
        # choice函数：每次从seeds拿一个值，加入列表
        for i in range(4):
            # 将列表里的值，变成四位字符串
            random_str.append(choice(seeds))
        return ''.join(random_str)

    # 直接复制CreateModelMixin中的create方法进行重写
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # raise_exception=True表示is_valid验证失败，就直接抛出异常，被drf捕捉到，直接会返回400错误，不会往下执行

        mobile = serializer.validated_data['mobile']  # 直接取mobile，上方无异常，那么mobile字段肯定是有的

        # 生成验证码
        code = self.generate_code()
        sendsms = send_sms(mobile=mobile, code=code)  # 模拟发送短信

        if sendsms.get('status_code') != 0:
            return Response({
                'mobile': sendsms['msg']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 在短信发送成功之后保存验证码
            code_record = VerifyCode(mobile=mobile, code=code)
            code_record.save()

            return Response({
                'mobile': mobile
            }, status=status.HTTP_201_CREATED)  # 可以创建成功代码为201

        # 以下就不需要了
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    create:
        创建用户

    retrieve:
        显示用户详情，仅能获取当前登录用户
    """
    # serializer_class = UserSerializer
    def get_serializer_class(self):
        """
        不同的action使用不同的序列化
        :return:
        """
        if self.action == 'retrieve':
            return UserDetailSerializer  # 使用显示用户详情的序列化类。这儿就直接返回类名，不需要实例化
        elif self.action == 'create':
            return UserSerializer  # 使用原来的序列化类，创建用户专用
        else:
            return UserDetailSerializer

    queryset = User.objects.all()
    authentication_classes = (SessionAuthentication, JWTAuthentication)  # 自定义VieSet认证方式：JWT用于前端登录认证，Session用于方便在DRF中调试使用

    # permissions = (permissions.IsAuthenticated,)  # 用户登录后才能获取详情，但用户注册也要求该权限，不可行
    def get_permissions(self):
        """
        动态设置不同action不同的权限类列表
        """
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]  # 一定要加()表明返回它的实例
        elif self.action == 'create':
            return []
        else:
            return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # 添加自己的逻辑，生成token并返回
        refresh = RefreshToken.for_user(user)
        tokens_for_user = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            # 数据定制化
            'username': user.username,  # 由于前端也需要传入username，需要将其加上。cookie.setCookie('name', response.data.username, 7);
        }

        headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # 在返回的时候就直接返回tokens_for_user
        return Response(tokens_for_user, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    def get_object(self):
        # 获取操作的对象，在RetrieveModelMixin和DestroyModelMixin都需要用到
        return self.request.user
