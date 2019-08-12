from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.permissions import IsOwnerOrReadOnly

from .serializers import ShoppingCartSerializer, ShoppingCartListSerializer, OrderInfoSerializer, OrderInfoDetailSerializer
from .models import ShoppingCart, OrderInfo, OrderGoods


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    购物车功能实现
    list:
        获取购物车列表
    create:
        添加商品到购物车
    update:
        更新购物车商品数量
    delete:
        从购物车中删除商品
    """
    # 权限问题：购物车和用户权限关联，这儿和用户操作差不多
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 用户必须登录才能访问
    authentication_classes = (JWTAuthentication, SessionAuthentication)  # 配置登录认证：支持JWT认证和DRF基本认证
    # serializer_class = ShoppingCartSerializer  # 使用get_serializer_class()，这个就不需要了
    queryset = ShoppingCart.objects.all()
    lookup_field = 'goods'

    def get_serializer_class(self):
        if self.action == 'list':
            # 当获取购物车列表时，使用ModelSerializer，可以显示购物车商品详情
            return ShoppingCartListSerializer
        else:
            return ShoppingCartSerializer

    def get_queryset(self):
        # 只能显示当前用户的购物车列表
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 添加到购物车，库存数减少
        shop_cart = serializer.save()
        goods = shop_cart.goods
        # 商品的库存量goods_num，减去购物车中的数量
        goods.goods_num -= shop_cart.nums
        goods.save()

    def perform_destroy(self, instance):
        # 从购物车中删除，库存量减少
        goods = instance.goods
        # 商品的库存量goods_num，加上删除的数量
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    def perform_update(self, serializer):
        # 更新购物车中数量，先获取原来的数量，再进行更新
        cart_goods = serializer.instance
        old_cart_goods_num = cart_goods.nums  # 获取购物车中该商品原来的数量
        update_cart_goods = serializer.save()
        diff_nums = update_cart_goods.nums - old_cart_goods_num  # 现在的数量减去以前的数量
        goods = cart_goods.goods
        # 得到商品对象，更改库存量
        goods.goods_num -= diff_nums
        goods.save()


class OrderInfoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    订单管理
    list:
        获取个人订单
    create:
        新建订单
    delete:
        删除订单
    detail:
        订单详情
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)  # 用户必须登录才能访问
    authentication_classes = (JWTAuthentication, SessionAuthentication)  # 配置登录认证：支持JWT认证和DRF基本认证
    queryset = OrderInfo.objects.all()
    # serializer_class = OrderInfoSerializer  # 添加序列化

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):  # 动态序列化，当显示订单详情，用另一个Serializer
        if self.action == 'retrieve':
            return OrderInfoDetailSerializer
        else:
            return OrderInfoSerializer

    def perform_create(self, serializer):
        # 完成创建后保存到数据库，可以拿到保存的值
        order = serializer.save()
        shopping_carts = ShoppingCart.objects.filter(user=self.request.user)
        # 将该用户购物车所有商品都取出来放在订单商品中
        for shopping_cart in shopping_carts:
            OrderGoods.objects.create(
                order=order,
                goods=shopping_cart.goods,
                goods_nums=shopping_cart.nums
            )
        # 然后清空该用户购物车
        shopping_carts.delete()

    def perform_destroy(self, instance):
        # 取消（删除）商品库存量增加
        for order_goods in instance.order_goods.all():
            goods = order_goods.goods
            # 获取订单商品的数量，修改库存量
            goods.goods_num += order_goods.goods_nums
            goods.save()
        instance.delete()


from rest_framework.views import APIView
from rest_framework.response import Response
from utils.alipay import AliPay, get_server_ip
from DjangoOnlineFreshSupermarket.settings import app_id, alipay_debug, alipay_public_key_path, app_private_key_path
from django.utils import timezone
from django.shortcuts import redirect, reverse


class AliPayView(APIView):
    def get(self, request):
        """
        处理支付宝return_url返回
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.GET.items():  # GET逻辑和POST基本一样
            processed_dict[key] = value

        print('request.GET的值：', processed_dict)
        sign = processed_dict.pop('sign', None)  # 直接就是字符串了

        server_ip = get_server_ip()
        alipay = AliPay(
            app_id=app_id,  # 自己支付宝沙箱 APP ID
            notify_url="http://{}:8000/alipay/return/".format(server_ip),
            app_private_key_path=app_private_key_path,  # 可以使用相对路径那个
            alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=alipay_debug,  # 默认False,
            return_url="http://{}:8000/alipay/return/".format(server_ip)
        )

        verify_result = alipay.verify(processed_dict, sign)  # 验证签名，如果成功返回True
        if verify_result:
            # POST中已经修改数据库订单状态，无需再GET中修改，且，GET中也得不到支付状态值

            # 给支付宝返回一个消息，证明已收到异步通知
            # return Response('success')
            # 修改为跳转到Vue页面
            response = redirect(reverse('index'))
            response.set_cookie('nextPath', 'pay', max_age=2)  # max_age设置为2s，让其快速过期，用一次就好了。
            # 跳转回Vue中时，直接跳转到Vue的pay的页面，后台无法配置，只能让Vue实现跳转。
            return response
        else:
            # 验证不通过直接跳转回首页就行，不设置cookie
            return redirect(reverse('index'))

    def post(self, request):
        """
        处理支付宝notify_url异步通知
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value

        print('request.POST的值：', processed_dict)
        sign = processed_dict.pop('sign', None)  # 直接就是字符串了

        server_ip = get_server_ip()
        alipay = AliPay(
            app_id=app_id,  # 自己支付宝沙箱 APP ID
            notify_url="http://{}:8000/alipay/return/".format(server_ip),
            app_private_key_path=app_private_key_path,  # 可以使用相对路径那个
            alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=alipay_debug,  # 默认False,
            return_url="http://{}:8000/alipay/return/".format(server_ip)
        )

        verify_result = alipay.verify(processed_dict, sign)  # 验证签名，如果成功返回True
        if verify_result:
            order_sn = processed_dict.get('out_trade_no')  # 原支付请求的商户订单号
            trade_no = processed_dict.get('trade_no')  # 支付宝交易凭证号
            trade_status = processed_dict.get('trade_status')  # 交易目前所处的状态

            # 更新数据库订单状态
            """
            OrderInfo.objects.filter(order_sn=order_sn).update(
                trade_no=trade_no,  # 更改交易号
                pay_status=trade_status,  # 更改支付状态
                pay_time=timezone.now()  # 更改支付时间
            )
            """
            orderinfos = OrderInfo.objects.filter(order_sn=order_sn)
            for orderinfo in orderinfos:
                orderinfo.trade_no = trade_no,  # 更改交易号
                orderinfo.pay_status = trade_status,  # 更改支付状态
                orderinfo.pay_time = timezone.now()  # 更改支付时间
                # 更改商品的销量
                order_goods = orderinfo.order_goods.all()
                for item in order_goods:
                    # 获取订单中商品和商品数量，然后将商品的销量进行增加
                    goods = item.goods
                    goods.sold_num += item.goods_nums
                    goods.save()

                orderinfo.save()

            # 给支付宝返回一个消息，证明已收到异步通知
            # 当商户收到服务器异步通知并打印出 success 时，服务器异步通知参数 notify_id 才会失效。
            # 也就是说在支付宝发送同一条异步通知时（包含商户并未成功打印出 success 导致支付宝重发数次通知），服务器异步通知参数 notify_id 是不变的。
            return Response('success')
