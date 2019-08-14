from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.permissions import IsOwnerOrReadOnly
from .serializers import UserFavSerializer, UserFavListSerializer, UserLeavingMessageSerializer, AddressSerializer
from .models import UserFav, UserLeavingMessage, UserAddress


class UserFavViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    create:
        用户收藏商品

    destroy:
        取消收藏商品

    list:
        显示收藏商品列表

    retrieve:
        根据商品id显示收藏详情
    """
    queryset = UserFav.objects.all()

    # serializer_class = UserFavSerializer
    def get_serializer_class(self):
        """
        不同的action使用不同的序列化
        :return:
        """
        if self.action == 'list':
            return UserFavListSerializer  # 显示用户收藏列表序列化
        else:
            return UserFavSerializer

    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JWTAuthentication, SessionAuthentication)  # 配置登录认证：支持JWT认证和DRF基本认证
    lookup_field = 'goods_id'

    def get_queryset(self):
        # 过滤当前用户的收藏记录
        return self.queryset.filter(user=self.request.user)

    """
    # 使用信号实现，该处代码不需要了
    def perform_create(self, serializer):
        # 添加收藏商品，商品收藏数+1
        # 序列化保存，然后将它赋值给一个实例，也就是UserFav(models.Model)对象
        instance = serializer.save()
        # 获取其中的商品
        goods = instance.goods
        # 商品收藏数+1
        goods.fav_num += 1
        goods.save()

    def perform_destroy(self, instance):
        # 删除收藏商品，商品收藏数-1
        goods = instance.goods
        # 商品收藏数-1
        goods.fav_num -= 1
        if goods.fav_num < 0:
            goods.fav_num = 0
        goods.save()
        instance.delete()
    """


class UserLeavingMessageViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    create:
        创建用户留言

    list:
        获取用户留言

    delete:
        删除用户留言
    """
    queryset = UserLeavingMessage.objects.all()
    serializer_class = UserLeavingMessageSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 用户必须登录才能访问
    authentication_classes = (JWTAuthentication, SessionAuthentication)  # 配置登录认证：支持JWT认证和DRF基本认证

    def get_queryset(self):
        """只查询当前登录用户"""
        return self.queryset.filter(user=self.request.user)


class AddressViewSet(viewsets.ModelViewSet):
    """
    收货地址管理
    list:
        获取收货地址
    create:
        添加收货地址
    update:
        更新收货地址
    delete:
        删除收货地址
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 用户必须登录才能访问
    authentication_classes = (JWTAuthentication, SessionAuthentication)  # 配置登录认证：支持JWT认证和DRF基本认证
    queryset = UserAddress.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class HotSearchView(APIView):
    def get(self, request):
        from utils.hotsearch import HotSearch
        from django.http import JsonResponse
        from rest_framework.response import Response
        from rest_framework import exceptions, status
        import json
        hot_search = HotSearch()
        result = []
        for keyword in hot_search.get_hotsearch():
            tmp = dict()
            tmp['keyword'] = keyword
            result.append(tmp)
        # return JsonResponse(result, safe=False)
        return Response(result, status=status.HTTP_200_OK)
