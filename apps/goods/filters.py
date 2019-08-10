from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Goods


class GoodsFilter(filters.FilterSet):
    """
    商品的过滤类
    """
    name = filters.CharFilter(field_name='name', lookup_expr='contains', help_text='分类名模糊匹配')  # 包含关系，模糊匹配
    goods_desc = filters.CharFilter(field_name='name', lookup_expr='contains', help_text='商品描述模糊匹配')
    min_price = filters.NumberFilter(field_name="shop_price", lookup_expr='gte', help_text='最低价格')  # 自定义字段
    max_price = filters.NumberFilter(field_name="shop_price", lookup_expr='lte', help_text='最高价格')
    top_category = filters.NumberFilter(method='top_category_filter', field_name='category_id', lookup_expr='=', help_text='自定义过滤某个一级分类')  # 自定义过滤，过滤某个一级分类

    def top_category_filter(self, queryset, field_name, value):
        """
        自定义过滤内容
        这儿是传递一个分类的id，在已有商品查询集基础上获取分类id，一级一级往上找，直到将三级类别找完
        :param queryset:
        :param field_name:
        :param value: 需要过滤的值
        :return:
        """
        queryset = queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(category__parent_category__parent_category_id=value))
        return queryset

    class Meta:
        model = Goods
        fields = ['name', 'goods_desc', 'min_price', 'max_price', 'is_hot', 'is_new']
