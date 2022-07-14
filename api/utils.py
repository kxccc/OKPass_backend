import re
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from okpass.settings import EMAIL_USER, EMAIL_PASSWORD
import redis
from okpass.settings import REDIS_HOST, REDIS_PORT, CAPTCHA_POOL, TOKEN_POOL
from rest_framework.response import Response

captcha_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, db=CAPTCHA_POOL)
token_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, db=TOKEN_POOL)


class CustomError(Exception):
    def __init__(self, error_info):
        super().__init__(self)
        self.error_info = error_info

    def __str__(self):
        return self.error_info


def check_password(test):
    if re.match(r'\S*\d+\S*', test) and re.match(r'\S*[a-z]+\S*', test) and re.match(r'\S*[A-Z]+\S*', test) and len(
            test) >= 8:
        return True
    return False


def send_mail(message, subject, sender_show, recipient_show, to_addr, cc_show=''):
    """
    :param message: str 邮件内容
    :param subject: str 邮件主题描述
    :param sender_show: str 发件人显示，不起实际作用如："xxx"
    :param recipient_show: str 收件人显示，不起实际作用，多个收件人用','隔开如："xxx,xxxx"
    :param to_addr: str 实际收件人
    :param cc_show: str 抄送人显示，不起实际作用，多个抄送人用','隔开如："xxx,xxxx"
    """
    # 填写真实的发邮件服务器用户名、密码
    user = EMAIL_USER
    password = EMAIL_PASSWORD
    # 邮件内容
    msg = MIMEText(message, 'plain', _charset="utf-8")
    # 邮件主题描述
    msg["Subject"] = subject
    # 发件人显示，不起实际作用
    msg["from"] = sender_show
    # 收件人显示，不起实际作用
    msg["to"] = recipient_show
    # 抄送人显示，不起实际作用
    msg["Cc"] = cc_show
    with SMTP_SSL(host="smtp.qq.com", port=465) as smtp:
        # 登录发邮件服务器
        smtp.login(user=user, password=password)
        # 实际发送、接收邮件配置
        smtp.sendmail(from_addr=user, to_addrs=[to_addr], msg=msg.as_string())


def check_captcha(email, captcha):
    r = redis.Redis(connection_pool=captcha_pool)
    if not r.exists(email):
        raise CustomError('验证码过期')
    elif r.get(email) != captcha:
        raise CustomError('验证码错误')
    r.delete(email)


def check_token(func):
    def improve(*args, **kwargs):
        try:
            token = args[1].data['token']
            r = redis.Redis(connection_pool=token_pool)
            dic = r.hgetall(token)
            email = dic['email']
            user_id = dic['user_id']
            random = dic['random']
            assert r.get(email) == random
            r.expire(token, 259200)
            args[1].data['email'] = email
            args[1].data['user_id'] = user_id
            return func(*args, **kwargs)
        except Exception as ex:
            print(ex)
        return Response(data={'status': False, 'msg': 'token失效'})

    return improve
