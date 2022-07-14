from rest_framework.views import APIView
from rest_framework.response import Response
import redis
import random
from .utils import CustomError, check_password, check_captcha, token_pool, check_token
from .models import User
from .serializers import UserSerializer
import rncryptor
from cryptography.fernet import Fernet
import base64
import uuid


class RegisterAPIView(APIView):
    def post(self, request):
        res = {'status': False, 'msg': '注册失败'}
        try:
            data = request.data
            email = data['email']
            password = data['password']
            captcha = data['captcha']

            q = User.objects.filter(email=email)
            if q.count() != 0:
                raise CustomError('邮箱已注册')

            check_captcha(email, captcha)

            if not check_password(password):
                raise CustomError('弱密码')

            key = Fernet.generate_key()
            key = str(key, encoding="utf-8")
            encrypted_key = rncryptor.encrypt(key, password)
            encrypted_key = base64.encodebytes(encrypted_key)
            encrypted_key = str(encrypted_key, encoding='utf-8')

            new_user = {
                "email": email,
                "key": encrypted_key,
                "random": random.randint(100, 999)
            }
            serializer = UserSerializer(data=new_user)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            res['status'] = True
            res['msg'] = '注册成功'
        except CustomError as e:
            print(e)
            res['msg'] = str(e)
        except Exception as e:
            print(e)
        return Response(data=res)


class LoginAPIView(APIView):
    def post(self, request):
        res = {'status': False, 'msg': '登录失败'}
        try:
            data = request.data
            email = data['email']
            password = data['password']
            captcha = data['captcha']

            q = User.objects.filter(email=email)
            if q.count() == 0:
                raise CustomError('邮箱未注册')

            check_captcha(email, captcha)

            encrypted_key = q[0].key
            encrypted_key = bytes(encrypted_key, encoding='utf-8')
            encrypted_key = base64.b64decode(encrypted_key)
            key = rncryptor.decrypt(encrypted_key, password)

            token = str(uuid.uuid4())
            r = redis.Redis(connection_pool=token_pool)
            dic = {
                "email": email,
                "user_id": q[0].id,
                "random": q[0].random
            }
            r.hmset(token, dic)
            r.expire(token, 259200)
            r.set(email, q[0].random)

            res['status'] = True
            res['msg'] = '登录成功'
            res['data'] = {}
            res['data']['token'] = token
            res['data']['key'] = key
        except rncryptor.DecryptionError as e:
            print(e)
            res['msg'] = "密码错误"
        except CustomError as e:
            print(e)
            res['msg'] = str(e)
        except Exception as e:
            print(e)
        return Response(data=res)


class PasswdAPIView(APIView):
    @check_token
    def post(self, request):
        res = {'status': False, 'msg': '修改失败'}
        try:
            data = request.data
            email = data['email']
            old_password = data['old_password']
            new_password = data['new_password']
            captcha = data['captcha']

            q = User.objects.filter(email=email)
            if q.count() == 0:
                raise CustomError('修改失败')

            check_captcha(email, captcha)

            if not check_password(new_password):
                raise CustomError('新密码弱')

            encrypted_key = q[0].key
            encrypted_key = bytes(encrypted_key, encoding='utf-8')
            encrypted_key = base64.b64decode(encrypted_key)
            key = rncryptor.decrypt(encrypted_key, old_password)
            encrypted_key = rncryptor.encrypt(key, new_password)
            encrypted_key = base64.encodebytes(encrypted_key)
            encrypted_key = str(encrypted_key, encoding='utf-8')

            old_random = q[0].random
            new_random = old_random
            while old_random == new_random:
                new_random = random.randint(100, 999)
            user = {
                "email": email,
                "key": encrypted_key,
                "random": new_random
            }
            serializer = UserSerializer(instance=q[0], data=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            r = redis.Redis(connection_pool=token_pool)
            r.set(email, new_random)

            res['status'] = True
            res['msg'] = '修改成功'
        except rncryptor.DecryptionError as e:
            print(e)
            res['msg'] = "旧密码错误"
        except CustomError as e:
            print(e)
            res['msg'] = str(e)
        except Exception as e:
            print(e)
        return Response(data=res)
