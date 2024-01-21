from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
import random
from receivers_selection_api.serializers import *
from receivers_selection_api.models import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from ..minio.minioClass import MinioClass
from ..filters import *
from ..permissions import *
from ..services import *
from drf_yasg.utils import swagger_auto_schema
from .viewSending import getSendingPositionsWithReceiverData
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    
def getProductDataWithImage(serializer: receiverSerializer):
    minio = MinioClass()
    ParticipantData = serializer.data
    ParticipantData.update({'img': minio.getImage('images', serializer.data['id'])})
    return ParticipantData

def postProductImage(request, serializer: receiverSerializer):
    minio = MinioClass()
    minio.addImage('images', serializer.data['id'], request.data['img'])

# изменяет картинку продукта в minio на переданную в request
def putProductImage(request, serializer: receiverSerializer):
    minio = MinioClass()
    minio.removeImage('images', serializer.data['id'])
    minio.addImage('images', serializer.data['id'], request.data['img'])

class process_Receiverlist(APIView):
    def get(self, request, format=None):
        sendingid = getSendingID(request)
        List = {
            'SendingId' : sendingid
        }
        Receivers = filterReceiver(receiver.objects.all(), request)
        ReceiversData = [getProductDataWithImage(receiverSerializer(Receiver)) for Receiver in Receivers]
        List ['Receivers'] = ReceiversData
        return Response(List, status=status.HTTP_202_ACCEPTED)
    
    @swagger_auto_schema(operation_description="Данный метод добавляет нового участника. Доступ: все.", request_body=receiverSerializer)
    def post(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        currentUser = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moder:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = receiverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postProductImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class procces_receiver_detail(APIView):
    def get(self, request, pk, format=None):
        Receiver = get_object_or_404(receiver,pk=pk)
        serializer = receiverSerializer(Receiver)
        return Response(getProductDataWithImage(serializer), status=status.HTTP_202_ACCEPTED)
    
    def post(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        username = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        SendingId = getSendingID(request)
        if SendingId == -1:   # если его нету
            request_new = sending.objects.create(
                user_name=username,
                moder_name=random.choice(user.objects.filter(is_moder=True))
            )
            SendingId = request_new.pk
            
        # теперь у нас точно есть черновик, поэтому мы создаём связь м-м (не уверен что следующие две строки вообще нужны)    
        if sending.objects.get(pk=SendingId).status != 'I' or len(sendingReceiver.objects.filter(Receiver=pk).filter(Sending=SendingId)) != 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        sendingReceiver.objects.create(
            Receiver_id=pk,
            Sending_id=SendingId,
            is_contact = False
        )
        
        request_new = sending.objects.get(pk=SendingId)
        requestserializer = sendingSerializer(request_new)

        positions = sendingReceiver.objects.filter(Sending=request_new.pk)
        positionsSerializer = PositionSerializer(positions, many=True)

        response = requestserializer.data
        response['positions'] = getSendingPositionsWithReceiverData(positionsSerializer)
        return Response(response, status=status.HTTP_202_ACCEPTED)
    
    def delete(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        currentUser = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moder:
            return Response(status=status.HTTP_403_FORBIDDEN)

        Receiver = get_object_or_404(receiver, pk=pk)
        Receiver.status = '0' if Receiver.status == '1' else '1'
        Receiver.save()
        serializer = receiverSerializer(Receiver)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=receiverSerializer)
    def put(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        currentUser = user.objects.get(username=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moder:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        product = get_object_or_404(receiver, pk=pk)
        fields = request.data.keys()
        if 'id' in fields or 'status' in fields or 'last_modified' in fields:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = receiverSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if 'img' in fields and fields.mapping['img'] != '':
                putProductImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
