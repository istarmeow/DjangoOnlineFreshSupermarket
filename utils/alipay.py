# -*- coding: utf-8 -*-

# pip install pycryptodome
__author__ = 'bobby'

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes
import json


class AliPay(object):
    """
    支付宝支付接口
    """

    def __init__(self, app_id, notify_url, app_private_key_path, alipay_public_key_path, return_url, debug=True):
        self.app_id = app_id  # 支付宝分配的应用ID
        self.notify_url = notify_url  # 支付宝服务器主动通知商户服务器里指定的页面http/https路径；用户一旦支付，会向该url发一个异步的请求给自己服务器，这个一定需要公网可访问
        self.app_private_key_path = app_private_key_path  # 个人私钥路径
        self.app_private_key = None  # 个人私钥内容
        self.return_url = return_url  # 网页上支付完成后跳转回自己服务器的url
        with open(self.app_private_key_path) as fp:
            # 读取个人私钥文件提取到私钥内容
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            # 读取支付宝公钥文件提取公钥内容，支付宝公钥在代码中验签使用
            self.alipay_public_key = RSA.import_key(fp.read())

        if debug is True:
            # 使用沙箱的网关
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {  # 请求参数的集合
            "subject": subject,  # 订单标题
            "out_trade_no": out_trade_no,  # 商户订单号,
            "total_amount": total_amount,  # 订单总金额
            "product_code": "FAST_INSTANT_TRADE_PAY",  # 销售产品码，默认
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)  # 合并其他请求参数字典
        data = self.build_body("alipay.trade.page.pay", biz_content, return_url)  # 将请求参数合并到公共参数字典的键biz_content中
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        """
        组合所有的请求参数到一个字典中
        :param method:
        :param biz_content:
        :param return_url:
        :return:
        """
        data = {
            "app_id": self.app_id,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is None:
            data["notify_url"] = self.notify_url
            data["return_url"] = self.return_url

        return data

    def ordered_data(self, data):
        """
        并按照第一个字符的键值ASCII码递增排序（字母升序排序），如果遇到相同字符则按照第二个字符的键值ASCII码递增排序，以此类推。
        :param data:
        :return: 返回的是数组列表，按照数据中的k进行排序的
        """
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        """
        使用各自语言对应的SHA256WithRSA(对应sign_type为RSA2)或SHA1WithRSA(对应sign_type为RSA)签名函数利用商户私钥对待签名字符串进行签名，并进行Base64编码。
        :param unsigned_string:
        :return:
        """
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def sign_data(self, data):
        """
        获取所有请求参数，不包括字节类型参数，如文件、字节流，剔除sign字段，剔除值为空的参数。
        进行排序。
        将排序后的参数与其对应值，组合成“参数=参数值”的格式，并且把这些参数用&字符连接起来，此时生成的字符串为待签名字符串。
        然后对该字符串进行签名。
        把生成的签名赋值给sign参数，拼接到请求参数中。
        :param data:
        :return:
        """
        data.pop("sign", None)
        # 排序后的字符串
        ordered_items = self.ordered_data(data)  # 数组列表，进行遍历拼接
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in ordered_items)  # 使用参数=值得格式用&连接

        sign = self.sign(unsigned_string.encode("utf-8"))  # 得到签名后的字符串
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in ordered_items)  # quote_plus给url进行预处理，特殊字符串在url中会有问题

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


def get_server_ip():
    """
    在项目根目录项创建ProjectConfig.ini配置文件，读取其中配置的IP地址
    :return:
    """
    import configparser
    import os
    import sys

    # 获取当前文件的路径（运行脚本）
    pwd = os.path.dirname(os.path.realpath(__file__))

    # 获取项目的根目录
    sys.path.append(pwd + "../")

    # 要想单独使用django的model，必须指定一个环境变量，会去settings配置找
    # 参照manage.py里面就知道为什么这样设置了
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoOnlineFreshSupermarket.settings')

    import django
    django.setup()
    from django.conf import settings

    config = configparser.ConfigParser()
    config.read(os.path.join(settings.BASE_DIR, 'ProjectConfig.ini'))
    server_ip = config['DjangoOnlineFreshSupermarket']['server_ip']
    return server_ip


if __name__ == "__main__":
    print(get_server_ip())
    server_ip = get_server_ip()  # 得到自己服务器的IP地址，也就是之前同步项目上去的
    alipay = AliPay(
        app_id="2016100900646609",  # 自己支付宝沙箱 APP ID
        notify_url="http://{}:8000/alipay/return/".format(server_ip),
        app_private_key_path="../apps/trade/keys/private_key_2048.txt",  # 可以使用相对路径那个
        alipay_public_key_path="../apps/trade/keys/alipay_key_2048.txt",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=True,  # 默认False,
        return_url="http://{}:8000/alipay/return/".format(server_ip)
    )

    # 创建订单
    url = alipay.direct_pay(
        subject="测试订单",
        out_trade_no="2019080716060015",
        total_amount=0.01,
        return_url="http://{}:8000/alipay/return/".format(server_ip)  # 支付完成后自动跳回该url
    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    print(re_url)

    # 支付成功后跳回的页面url
    return_url = "http://118.25.208.30:8000/?charset=utf-8&out_trade_no=2019080716060003&method=alipay.trade.page.pay.return&total_amount=0.01&sign=Ej1B3IHs4q6aaWXLqwphXelaPcrok%2Ft7FPmFwns368fc6LcDfvLgBFAqsVwryWMJmHddwiiGgDDSkJKl0f30dYyS0mh9HXlbAXacUJgHHRUvsrN9BiJ9GBoLf%2FInKXcC6n7bqkSDORW1Rnn2N1354NieHVW9W67dNhHCN%2FnpVzALX2c%2F5g7z06i1aYIdLVDfUsXVzn2fDGhZ%2BAHYoFoDKMTr0kFuPGSNPnt8%2F0Q75je8%2BbWmF%2BXMOm1152wVHUMyL1LEO9n9NDba1IPTLWBzlw11CM4eFIIZrTWheCKuACrrNAGDLDSMtDIKwsOWuGY8Z1DCODerGR8Mqbprx%2BSGLQ%3D%3D&trade_no=2019080722001421571000030866&auth_app_id=2016100900646609&version=1.0&app_id=2016100900646609&sign_type=RSA2&seller_id=2088102178762103&timestamp=2019-08-07+16%3A31%3A37"

    # 根据返回的链接，测试验证签名
    o = urlparse(return_url)
    query = parse_qs(o.query)

    # 获取url返回的签名sign
    ali_sign = query.pop("sign")[0]

    processed_query = {}
    for key, value in query.items():
        print('{}：{}'.format(key, value))
        processed_query[key] = value[0]
        # 可以提取到响应参数值
        """
        charset：['utf-8']
        out_trade_no：['2019080716060003']
        method：['alipay.trade.page.pay.return']
        total_amount：['0.01']
        trade_no：['2019080722001421571000030866']
        auth_app_id：['2016100900646609']
        version：['1.0']
        app_id：['2016100900646609']
        sign_type：['RSA2']
        seller_id：['2088102178762103']
        timestamp：['2019-08-07 16:31:37']
        """
    print(alipay.verify(processed_query, ali_sign))
