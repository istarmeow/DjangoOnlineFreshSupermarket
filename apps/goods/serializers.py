from rest_framework import serializers
from .models import Goods, GoodsCategory, GoodsImage, Banner, GoodsCategoryBrand
from django.db.models import Q


class CategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class CategorySerializer2(serializers.ModelSerializer):
    sub_category = CategorySerializer3(many=True)  # 通过二级分类获取三级分类

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    sub_category = CategorySerializer2(many=True)  # 通过一级分类获取到二级分类，由于一级分类下有多个二级分类，需要设置many=True

    class Meta:
        model = GoodsCategory
        fields = '__all__'


# 商品图片序列化
class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ['image']  # 需要的字段只需要image


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # 自定义字段覆盖原有的字段，实例化
    images = GoodsImageSerializer(many=True)  # 字段名和外键名称一样，商品轮播图，需要加many=True，因为一个商品有多个图片

    class Meta:
        model = Goods
        fields = '__all__'


# 获取父级分类
class ParentCategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class ParentCategorySerializer2(serializers.ModelSerializer):
    parent_category = ParentCategorySerializer3()

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class ParentCategorySerializer(serializers.ModelSerializer):
    parent_category = ParentCategorySerializer2()

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"


# 品牌图片
class BrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = "__all__"


# 首页分类商品序列化
class IndexCategoryGoodsSerializer(serializers.ModelSerializer):
    brands = BrandsSerializer(many=True)  # 分类下的品牌图片
    # goods = GoodsSerializer(many=True)  # 不能这样用，因为现在需要的是一级分类，而大多数商品是放在三级分类中的，所以很多商品是取不到的，所以到自己查询一级分类子类别下的所有商品
    goods = serializers.SerializerMethodField()
    sub_category = CategorySerializer2(many=True)  # 序列化二级分类
    ad_goods = serializers.SerializerMethodField()  # 广告商品可能加了很多，取每个分类第一个

    def get_ad_goods(self, obj):
        all_ads = obj.ads.all()
        if all_ads:
            ad = all_ads.first().goods  # 获取到商品分类对应的商品
            ad_serializer = GoodsSerializer(ad, context={'request': self.context['request']})  # 序列化该广告商品，嵌套的序列化类中添加context参数，可在序列化时添加域名
            return ad_serializer.data
        else:
            # 在该分类没有广告商品时，必须要返回空字典，否则Vue中取obj.id会报错
            return {}

    def get_goods(self, obj):
        # 查询每级分类下的所有商品
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__parent_category_id=obj.id) | Q(category__parent_category__parent_category_id=obj.id))
        # 将查询的商品集进行序列化
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})
        # 返回json对象
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = '__all__'
