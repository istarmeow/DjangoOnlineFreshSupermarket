import json
import re
import requests
from urllib.parse import urlencode, parse_qs


class OAuth_Weibo(object):
    def __init__(self, client_id, client_secret, redirect_uri, state):
        self.client_id = client_id  # 申请应用时分配的AppKey。
        self.client_secret = client_secret  # 申请的密钥
        self.redirect_uri = redirect_uri  # 授权回调地址，站外应用需与设置的回调地址一致，站内应用需填写canvas page的地址。
        self.state = state  # 防跨域攻击，随机码
        self.access_token = ''  # 获取到的token，初始化为空
        self.uid = ''  # 记录用户id

    def get_auth_url(self):
        """
        登录时，获取认证的url，跳转到该url进行github认证
        :return: https://api.weibo.com/oauth2/authorize?client_id=********&redirect_uri=http://1270.0.1:8000/oauth/weibo_check&state=******
        """
        auth_url = "https://api.weibo.com/oauth2/authorize"

        params = {
            'client_id': self.client_id,  # 申请应用时分配的AppKey。
            'redirect_uri': self.redirect_uri,  # 授权回调地址，站外应用需与设置的回调地址一致，站内应用需填写canvas page的地址。
            'state': self.state  # 不可猜测的随机字符串。它用于防止跨站点请求伪造攻击。
        }

        url = "{}?{}".format(auth_url, urlencode(params))  # urlencode将字典拼接成url参数
        # print(url)
        return url

    def get_access_token(self, code):
        """
        认证通过后，生成code，放在url中，视图中获取这个code，调用该函数，post提交请求token，最终得到token
        :param code: get_auth_url这一步中认证通过后，跳转回来的url中的code，10分钟过期。
        :return:
        """
        access_token_url = 'https://api.weibo.com/oauth2/access_token'

        data = {
            'client_id': self.client_id,  # 申请应用时分配的AppKey。
            'client_secret': self.client_secret,  # 申请应用时分配的AppSecret。
            'grant_type': 'authorization_code',  # 请求的类型，填写authorization_code
            'code': code,  # 调用authorize获得的code值，请求get_auth_url的地址返回的值。
            'redirect_uri': self.redirect_uri,  # 授回调地址，需需与注册应用里的回调地址一致。
        }

        r = requests.post(access_token_url, data=data)
        # print(r.text)  # '{"access_token":"2.00Ph1u5ChenG9C41634ac9ad_Q9o2D","remind_in":"157679999","expires_in":157679999,"uid":"2200323657","isRealName":"true"}'
        res = json.loads(r.text)
        if 'error' in res:
            # token错误
            print(res['error_description'])
        else:
            self.access_token = res['access_token']
            self.uid = res['uid']

        return self.access_token

    def get_user_info(self):
        """
        根据token和uid获取用户信息
        :return:
        """
        user_info_url = 'https://api.weibo.com/2/users/show.json'

        params = {'access_token': self.access_token, 'uid': self.uid}  # 根据token获取用户信息

        r = requests.get(user_info_url, params=params)
        # print(r.json())
        return r.json()


if __name__ == '__main__':
    app_key = '224xxx919'
    app_secret = 'bd43cebdxxxxxxxxc093xxxxxxxx513a'
    redirect_uri = 'http://127.0.0.1:8000/oauth/weibo_check'
    state = 'hj*&(hkjhfs76^hJHKULKG89798we'

    oauth = OAuth_Weibo(client_id=app_key, client_secret=app_secret, redirect_uri=redirect_uri, state=state)
    auth_url = oauth.get_auth_url()
    print(auth_url)
    # 访问该页面进行授权认证
    # 完成后跳回本地URL：http://127.0.0.1:8000/oauth/weibo_check?state=hj%2A%26%28hkjhfs76%5EhJHKULKG89798we&code=3b108579d3f025811ca22e79d4b62bed

    # 本地获取到url的参数值，判断return_state是否和以前的state相等
    return_state = 'hj%2A%26%28hkjhfs76%5EhJHKULKG89798we'
    return_code = '3b108579d3f025811ca22e79d4b62bed'  # 使用code来获取token，code只能使用一次，使用后失效

    access_token = oauth.get_access_token(code=return_code)  # 将token和uid保存在类中
    print(access_token)

    user_info = oauth.get_user_info()  # 根据token和uid获取用户信息，最终用户把这些信息保存在session中，
    print(user_info)
    # 通过 user_info['name'] 获取该用户昵称
