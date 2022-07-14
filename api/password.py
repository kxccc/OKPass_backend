from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PasswordSerializer
from .utils import check_token
from .models import Password


class PasswordAPIView(APIView):
    @check_token
    def post(self, request):
        res = {'status': False, 'msg': '添加失败'}
        try:
            serializer = PasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            res['status'] = True
            res['msg'] = '添加成功'
            res['id'] = serializer.data['id']
        except Exception as e:
            print(e)
        return Response(data=res)

    @check_token
    def delete(self, request):
        res = {'status': False, 'msg': '删除失败'}
        try:
            user_id = request.data['user_id']
            password_id = request.data['id']
            Password.objects.get(id=password_id, user_id=user_id).delete()

            res['status'] = True
            res['msg'] = '删除成功'
        except Exception as e:
            print(e)
        return Response(data=res)

    @check_token
    def put(self, request):
        res = {'status': False, 'msg': '修改失败'}
        try:
            user_id = request.data['user_id']
            password_id = request.data['id']
            q = Password.objects.get(id=password_id, user_id=user_id)
            serializer = PasswordSerializer(instance=q, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            res['status'] = True
            res['msg'] = '修改成功'
        except Exception as e:
            print(e)
        return Response(data=res)


class AllPasswordAPIView(APIView):
    @check_token
    def post(self, request):
        res = {'status': False, 'msg': '获取失败'}
        try:
            user_id = request.data['user_id']
            q = Password.objects.filter(user_id=user_id).order_by('-id')
            serializer = PasswordSerializer(instance=q, many=True)
            res['status'] = True
            res['msg'] = '获取成功'
            res['data'] = serializer.data
        except Exception as e:
            print(e)
        return Response(data=res)
