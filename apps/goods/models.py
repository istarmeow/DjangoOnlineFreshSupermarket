from django.db import models
from ckeditor.fields import RichTextField  # 文本编辑器
from ckeditor_uploader.fields import RichTextUploadingField  # 富文本可上传图片


class GoodsCategory(models.Model):
    """
    商品类别
    """
    CATEGORY_TYPE = (
        (1, '一级类目'),
        (2, '二级类目'),
        (3, '三级类目'),
    )
    name = models.CharField(max_length=30, default='', verbose_name='类别名称', help_text='商品类别名称')  # help_text说明，生成文档很有用
    code = models.CharField(max_length=30, default='', verbose_name='类别编码', help_text='商品类别编码')
    desc = models.TextField(default='', verbose_name='类别描述', help_text='类别描述')
    category_type = models.SmallIntegerField(choices=CATEGORY_TYPE, default=1, verbose_name='类目级别', help_text='商品类目的级别')
    is_tab = models.BooleanField(default=False, verbose_name='是否导航', help_text='类别是否导航')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    parent_category = models.ForeignKey('self', null=True, blank=True, verbose_name='父级目录', help_text='父级目录', on_delete=models.CASCADE, related_name='sub_category')

    class Meta:
        verbose_name_plural = verbose_name = '商品类别'

    def __str__(self):
        return self.name


class GoodsCategoryBrand(models.Model):
    """
    品牌
    """
    category = models.ForeignKey(GoodsCategory, null=True, blank=True, on_delete=models.CASCADE, verbose_name='商品类别', help_text='商品类别', related_name='brands')
    name = models.CharField(max_length=30, default='', verbose_name='品牌名称', help_text='品牌名称')
    desc = models.TextField(default='', max_length=200, verbose_name='品牌描述', help_text='品牌描述')
    image = models.ImageField(max_length=200, upload_to='brand/images/', verbose_name='品牌图片', help_text='品牌图片')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '品牌'

    def __str__(self):
        return self.name


class Goods(models.Model):
    """
    商品
    """
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='商品类别', help_text='商品类别', related_name='goods')
    goods_sn = models.CharField(max_length=100, default='', verbose_name='商品编码', help_text='商品唯一货号')
    name = models.CharField(max_length=300, verbose_name='商品名称', help_text='商品名称')
    click_num = models.IntegerField(default=0, verbose_name='点击数', help_text='点击数')
    sold_num = models.IntegerField(default=0, verbose_name='销售量', help_text='销售量')
    fav_num = models.IntegerField(default=0, verbose_name='收藏数', help_text='收藏数')
    goods_num = models.IntegerField(default=0, verbose_name='库存量', help_text='库存量')
    market_price = models.FloatField(default=0, verbose_name='市场价格', help_text='市场价格')
    shop_price = models.FloatField(default=0, verbose_name='本店价格', help_text='本店价格')
    goods_brief = models.TextField(max_length=500, verbose_name='简短描述', help_text='商品简短描述')
    goods_desc = RichTextUploadingField(verbose_name='详情描述', help_text='详情描述')
    ship_free = models.BooleanField(default=True, verbose_name='是否免运费', help_text='是否免运费')
    goods_front_image = models.ImageField(upload_to='goods/front/', null=True, blank=True, verbose_name='封面图', help_text='封面图')
    is_new = models.BooleanField(default=False, verbose_name='是否新品', help_text='是否新品')
    is_hot = models.BooleanField(default=False, verbose_name='是否热销', help_text='是否热销')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '商品'

    def __str__(self):
        return self.name


class GoodsImage(models.Model):
    """
    商品图片
    """
    goods = models.ForeignKey(Goods, verbose_name='商品', help_text='商品', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='goods/images/', verbose_name='图片', help_text='图片')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '商品图片'

    def __str__(self):
        return self.goods.name


class Banner(models.Model):
    """
    首页轮播图
    """
    goods = models.ForeignKey(Goods, verbose_name='商品', help_text='商品', on_delete=models.CASCADE, related_name='banners')
    image = models.ImageField(upload_to='goods/banners/', verbose_name='图片', help_text='图片')
    index = models.IntegerField(default=0, verbose_name='轮播顺序', help_text='轮播顺序')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '首页轮播图'

    def __str__(self):
        return self.goods.name


class IndexCategoryAd(models.Model):
    """
    首页广告
    """
    category = models.ForeignKey(GoodsCategory, null=True, blank=True, on_delete=models.CASCADE, verbose_name='商品类别', help_text='商品类别', related_name='ads')
    goods = models.ForeignKey(Goods, verbose_name='商品', help_text='商品', on_delete=models.CASCADE, related_name='ads')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name_plural = verbose_name = '首页类别广告'

    def __str__(self):
        return '{}：{}'.format(self.category.name, self.goods.name)
