from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from datetime import datetime
from ..minio.minioClass import MinioClass
from ..filters import *
from ..permissions import *
from ..services import *
from drf_yasg.utils import swagger_auto_schema
import requests
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

def checkStatusUpdate(old, new, isModer):
    return ((not isModer) and (new in ['P', 'D']) and (old == 'I')) or (isModer and (new in ['A', 'W']) and (old == 'P'))

def getReceiverInSendingWithImage(serializer: receiverSerializer):
    minio = MinioClass()
    receiverData = serializer.data
    receiverData.update({'img': minio.getImage('images', serializer.data['id'])})
    return receiverData
def getSendingPositionsWithReceiverData(serializer: PositionSerializer):
    positions = []
    for item in serializer.data:
        Receiver = get_object_or_404(receiver, pk=item['Receiver'])
        positionData = item
        positionData['receiver_data'] = getReceiverInSendingWithImage(receiverSerializer(Receiver))
        positions.append(positionData)
    return positions

class Current_Inp_View(APIView):
    @swagger_auto_schema(operation_description="Данный метод возвращает черновую заявку. Доступ: только если авторизован.")
    def get(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        username = session_storage.get(session_id)
        if username is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        currentUser = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        request_current = sending.objects.filter(user_name=currentUser).filter(status='I')
        if request_current.exists():
            application = request_current.first()
            requestserializer = sendingSerializer(application)

            positions = sendingReceiver.objects.filter(Sending=application.pk)
            positionsSerializer = PositionSerializer(positions, many=True)

            response = requestserializer.data
            response['positions'] = getSendingPositionsWithReceiverData(positionsSerializer)

            return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
class process_SendingList(APIView):

    # получение списка заказов
    def get(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        login1 = session_storage.get(session_id)
        if login1 is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        currentUser = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if currentUser.is_moder:
            orders = filterSending(sending.objects.all(), request)
        else:
            orders = filterSending(sending.objects.filter(user_name=currentUser.pk), request)
        serializer = sendingSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    # отправка заказа пользователем
    @swagger_auto_schema(request_body=sendingSerializer)
    def put(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        application = get_object_or_404(sending, pk=getSendingID(request))
        new_status = "P"
        if checkStatusUpdate(application.status, new_status, isModer=False):
            url = "http://localhost:8080/send/"
            params = {"id_sending": str(application.pk)}
            response = requests.post(url, json=params)
            application.status = new_status
            application.sent = datetime.now()
            application.save()
            serializer = sendingSerializer(application)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление заказа пользователем
    def delete(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        new_status = "D"
        application = get_object_or_404(sending, pk=getSendingID(request))
        if checkStatusUpdate(application.status, new_status, isModer=False):
            application.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class process_sending_detail(APIView):

    # получение заказа
    def get(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        currentUser = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        sending_keys = sending.objects.filter(user_name=currentUser).values_list('pk', flat=True)
        if (pk in sending_keys) or currentUser.is_moder:
            Sending1 = get_object_or_404(sending, pk=pk)
            SendingSerializer = sendingSerializer(Sending1)

            positions = sendingReceiver.objects.filter(Sending=pk)
            positionsSerializer = PositionSerializer(positions, many=True)

            response = SendingSerializer.data
            response['positions'] = getSendingPositionsWithReceiverData(positionsSerializer)

            return Response(response, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_403_FORBIDDEN)
    
     # перевод заказа модератором на статус A или W
    @swagger_auto_schema(request_body=sendingSerializer)
    def put(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        currentUser = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moder:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        Sending = get_object_or_404(sending, pk=pk)
        try: 
            new_status = request.data['status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if checkStatusUpdate(Sending.status, new_status, isModer=True):
            Sending.status = new_status
            Sending.received = datetime.now()
            Sending.save()
            serializer = sendingSerializer(Sending)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
   
        