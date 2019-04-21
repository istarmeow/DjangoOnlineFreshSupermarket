from django.views.generic.base import View
from django.views.generic import ListView
from goods.models import Goods


class GoodsListView(View):
    def get(self, request):
        """
        通过Django的View获取商品列表页
        :param request:
        :return:
        """
        json_list = list()
        all_goods = Goods.objects.all()[:5]
        # print(all_goods)
        # for goods in all_goods:
        #     json_dict = dict()
        #     json_dict['name'] = goods.name
        #     json_dict['category'] = goods.category.name
        #     json_dict['shop_price'] = goods.shop_price
        #     json_list.append(json_dict)

        # from django.forms.models import model_to_dict
        # for goods in all_goods:
        #     json_dict = model_to_dict(instance=goods)
        #     json_list.append(json_dict)

        from django.core import serializers
        json_data = serializers.serialize('json', all_goods)  # 序列化

        from django.http import HttpResponse, JsonResponse
        import json
        # return HttpResponse(json_data, content_type='application/json')
        json_data = json.loads(json_data)  # 转换为数组
        return JsonResponse(json_data, safe=False)

