# 这个用于模拟短信发送，直接在后端输出显示验证码内容


def send_sms(mobile, code):
    """
    调用短信服务商API发送短信逻辑
    :param mobile:
    :param code:
    :return:
    """
    print('\n\n【生鲜电商】你的验证码为：{}\n\n'.format(code))

    return {'status_code': 0, 'msg': '短信发送成功'}
