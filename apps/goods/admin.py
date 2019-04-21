from django.contrib import admin
from .models import GoodsCategory, Goods
from django.apps import apps


@admin.register(GoodsCategory)
class GoodsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_tab', 'parent_category']  # 列表页显示
    list_display_links = ('name', 'parent_category',)  # 列表页外键链接，字段需在list_display中
    list_editable = ('is_tab',)  # 列表页可编辑
    list_filter = ('category_type',)  # 列表页可筛选
    search_fields = ('name', 'desc')  # 列表页可搜索


all_models = apps.get_app_config('goods').get_models()
for model in all_models:
    try:
        admin.site.register(model)
    except:
        pass
