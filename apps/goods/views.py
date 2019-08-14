from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from .models import Goods, GoodsCategory, Banner
from .serializers import GoodsSerializer, CategorySerializer, ParentCategorySerializer, BannerSerializer, IndexCategoryGoodsSerializer
from .filters import GoodsFilter
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class GoodsPagination(PageNumberPagination):
    page_size = 12  # 每一页个数，由于前段
    page_query_description = _('使用分页后的页码')  # 分页文档中文描述
    page_size_query_param = 'page_size'
    page_size_query_description = _('每页返回的结果数')
    page_query_param = 'page'  # 参数?p=xx，将其修改为page，适应前端，也方便识别
    max_page_size = 36  # 最大指定每页个数


class GoodsListView(generics.ListAPIView):
    """
    显示所有的商品列表
    """
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination


class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        显示商品列表，分页、过滤、搜索、排序

    retrieve:
        显示商品详情
    """
    queryset = Goods.objects.all()  # 使用get_queryset函数，依赖queryset的值
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)  # 将过滤器后端添加到单个视图或视图集
    filterset_class = GoodsFilter
    # authentication_classes = (TokenAuthentication, )  # 只在本视图中验证Token
    search_fields = ('name', 'goods_desc', 'category__name')  # 搜索字段
    ordering_fields = ('click_num', 'sold_num', 'shop_price')  # 排序
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]  # DRF默认限速类，可以仿照写自己的限速类
    throttle_scope = 'goods_list'

    def retrieve(self, request, *args, **kwargs):
        # 增加点击数
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        keyword = self.request.query_params.get('search')
        if keyword:
            from utils.hotsearch import HotSearch
            hot_search = HotSearch()
            hot_search.save_keyword(keyword)
        return self.queryset


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # 注释很有用，在drf文档中
    """
    list:
        商品分类列表

    retrieve:
        商品分类详情
    """
    # queryset = GoodsCategory.objects.all()  # 取出所有分类，没必要分页，因为分类数据量不大
    queryset = GoodsCategory.objects.filter(category_type=1)  # 只获取一级分类数据
    serializer_class = CategorySerializer  # 使用商品类别序列化类，写商品的分类外键已有，直接调用


class ParentCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        根据子类别查询父类别

    retrieve:
        根据子类别查询父类别详情
    """
    queryset = GoodsCategory.objects.all()
    serializer_class = ParentCategorySerializer


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取轮播图列表
    """
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer


class IndexCategoryGoodsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
        首页分类、商品数据
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = IndexCategoryGoodsSerializer

    def get_queryset(self):
        # 随机取出几个分类
        import random
        category_id_list = self.queryset.values_list('id', flat=True)
        selected_ids = random.sample(list(category_id_list), 3)
        qs = self.queryset.filter(id__in=selected_ids)
        return qs