from django.contrib.auth import authenticate, logout
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema

from datetime import timedelta

import uuid

from ..serializers import *
from rest_framework.decorators import api_view
from receivers_selection_api.permissions import *
from ..services import get_session

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


class UserViewSet(ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = user.objects.all()
    serializer_class = userSerializer
    model_class = user

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsModerator]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request username ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(username=request.data['username']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self.model_class.objects.create_user(username=serializer.data['username'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'],
                                     is_moder=serializer.data['is_moder'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['Post'])
@permission_classes([IsAuthenticated])
def check(request):
    session_id = request.headers.get("authorization")

    if session_storage.get(session_id):
        User = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        serializer = userSerializer(User, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(method='post', request_body=userSerializer)
@api_view(['Post'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data["username"]
    password = request.data["password"]
    User: user = authenticate(request, username=username, password=password)

    if User is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)

        data = {
            "session_id": random_key,
            "user_id": User.pk,
            "username": User.username,
            "is_moderator": User.is_moder
        }

        response = Response(data, status=status.HTTP_201_CREATED)
        response.set_cookie("session_id", random_key, httponly=False, expires=timedelta(days=1))
        return response
    else:
        data ={
            "илья ты даун ебанный сколько можно уже"
        }
        return HttpResponse(data, status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(method='post')
@api_view(['Post'])
@permission_classes([AllowAny])
def logout_view(request):
    ssid = get_session(request)
    if ssid is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_storage.delete(ssid)

    logout(request._request)
    response = HttpResponse(status=status.HTTP_200_OK)
    response.delete_cookie("session_id")
    return response