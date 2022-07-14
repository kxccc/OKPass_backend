from smtplib import SMTPRecipientsRefused
from .utils import CustomError
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import send_mail
import redis
import random
from okpass.settings import REDIS_HOST, REDIS_PORT, CAPTCHA_POOL
from .models import User

captcha_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, db=CAPTCHA_POOL)


class RegisterCaptchaAPIView(APIView):
    def post(self, request):
        res = {'status': False, 'msg': '获取失败'}
        try:
            data = request.data
            email = data['email']
            captcha = random.randint(100000, 999999)

            q = User.objects.filter(email=email)
            if q.count() != 0:
                raise CustomError('邮箱已注册')

            r = redis.Redis(connection_pool=captcha_pool)
            if r.exists(email):
                raise CustomError('获取频繁，请一分钟后再试')

            message = '您正在注册OKPass，验证码为：{}，有效期1分钟'.format(captcha)
            subject = 'OKPass验证码'
            sender_show = 'OKPass'
            recipient_show = email
            to_addr = email
            send_mail(message, subject, sender_show, recipient_show, to_addr)

            r.set(email, captcha, ex=60)

            res['status'] = True
            res['msg'] = '获取成功'
        except SMTPRecipientsRefused as e:
            print(e)
            res['msg'] = '邮箱格式不对'
        except CustomError as e:
            print(e)
            res['msg'] = str(e)
        except Exception as e:
            print(e)
        return Response(data=res)


class CaptchaAPIView(APIView):
    def post(self, request):
        res = {'status': False, 'msg': '获取失败'}
        try:
            data = request.data
            email = data['email']
            captcha = random.randint(100000, 999999)

            q = User.objects.filter(email=email)
            if q.count() == 0:
                raise CustomError('邮箱未注册')

            r = redis.Redis(connection_pool=captcha_pool)
            if r.exists(email):
                raise CustomError('获取频繁，请一分钟后再试')

            message = '您的OKPass验证码为：{}，有效期1分钟'.format(captcha)
            subject = 'OKPass验证码'
            sender_show = 'OKPass'
            recipient_show = email
            to_addr = email
            send_mail(message, subject, sender_show, recipient_show, to_addr)

            r.set(email, captcha, ex=60)

            res['status'] = True
            res['msg'] = '获取成功'
        except CustomError as e:
            print(e)
            res['msg'] = str(e)
        except Exception as e:
            print(e)
        return Response(data=res)
