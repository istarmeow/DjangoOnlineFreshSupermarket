from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.permissions import IsOwnerOrReadOnly
from .serializers import UserFavSerializer
from .models import UserFav


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
    serializer_class = UserFavSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JWTAuthentication, SessionAuthentication)  # 配置登录认证：支持JWT认证和DRF基本认证
    lookup_field = 'goods_id'

    def get_queryset(self):
        # 过滤当前用户的收藏记录
        return self.queryset.filter(user=self.request.user)
