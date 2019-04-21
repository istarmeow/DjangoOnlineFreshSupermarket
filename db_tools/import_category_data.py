# 独立使用django的model
import sys
import os

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoOnlineFreshSupermarket.settings")

import django

django.setup()

from goods.models import GoodsCategory
from db_tools.data.category_data import row_data

# 清空
# GoodsCategory.objects.all().delete()

for lev1_cat in row_data:
    if not GoodsCategory.objects.filter(code=lev1_cat["code"], name=lev1_cat["name"], category_type=1):
        lev1_intance = GoodsCategory()
        lev1_intance.code = lev1_cat["code"]
        lev1_intance.name = lev1_cat["name"]
        lev1_intance.category_type = 1
        lev1_intance.save()
    else:
        lev1_intance = GoodsCategory.objects.get(code=lev1_cat["code"], name=lev1_cat["name"], category_type=1)

    for lev2_cat in lev1_cat["sub_categories"]:
        if not GoodsCategory.objects.filter(code=lev2_cat["code"], name=lev2_cat["name"], category_type=2):
            lev2_intance = GoodsCategory()
            lev2_intance.code = lev2_cat["code"]
            lev2_intance.name = lev2_cat["name"]
            lev2_intance.category_type = 2
            lev2_intance.parent_category = lev1_intance
            lev2_intance.save()
        else:
            lev2_intance = GoodsCategory.objects.get(code=lev2_cat["code"], name=lev2_cat["name"], category_type=2)

        for lev3_cat in lev2_cat["sub_categories"]:
            if not GoodsCategory.objects.filter(code=lev3_cat["code"], name=lev3_cat["name"], category_type=3):
                lev3_intance = GoodsCategory()
                lev3_intance.code = lev3_cat["code"]
                lev3_intance.name = lev3_cat["name"]
                lev3_intance.category_type = 3
                lev3_intance.parent_category = lev2_intance
                lev3_intance.save()
            else:
                lev3_intance = GoodsCategory.objects.get(code=lev3_cat["code"], name=lev3_cat["name"], category_type=3)
