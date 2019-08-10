from django.contrib import admin
from .models import GoodsCategory, Goods, GoodsImage, IndexCategoryAd
from django.apps import apps


@admin.register(GoodsCategory)
class GoodsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_tab', 'parent_category']  # 列表页显示
    list_display_links = ('name', 'parent_category',)  # 列表页外键链接，字段需在list_display中
    list_editable = ('is_tab',)  # 列表页可编辑
    list_filter = ('category_type',)  # 列表页可筛选
    search_fields = ('name', 'desc')  # 列表页可搜索


class GoodsImageInline(admin.TabularInline):
    model = GoodsImage


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [
        GoodsImageInline
    ]


@admin.register(IndexCategoryAd)
class IndexCategoryAdAdmin(admin.ModelAdmin):
    list_display = ['category', 'goods']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            # 外键下拉框添加过滤
            kwargs['queryset'] = GoodsCategory.objects.filter(category_type=1)
        return super(IndexCategoryAdAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


all_models = apps.get_app_config('goods').get_models()
for model in all_models:
    try:
        admin.site.register(model)
    except:
        pass
