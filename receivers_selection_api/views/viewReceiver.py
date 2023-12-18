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

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    
def getProductDataWithImage(serializer: receiverSerializer):
    minio = MinioClass()
    receiverData = serializer.data
    receiverData.update({'img': minio.getImage('images', serializer.data['id'])})
    return receiverData

def postProductImage(request, serializer: receiverSerializer):
    minio = MinioClass()
    image_file = request.FILES.get('image')
    byte_image = image_file.read()
    minio.addImage('images', serializer.data['id'], byte_image)

def putProductImage(request, serializer: receiverSerializer):
    minio = MinioClass()
    minio.removeImage('images', serializer.data['id'])
    minio.addImage('images', serializer.data['id'], request.data['image'])

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
    
    @method_permission_classes((IsModerator,))
    @swagger_auto_schema(request_body=receiverSerializer)
    def post(self, request, format=None):
        serializer = receiverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postProductImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class procces_receiver_detail(APIView):
    def get(self, pk, format=None):
        Receiver = get_object_or_404(receiver,pk=pk)
        serializer = receiverSerializer(Receiver)
        return Response(getProductDataWithImage(serializer), status=status.HTTP_202_ACCEPTED)
    
    def post(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        userId = user.objects.get(login=session_storage.get(session_id).decode('utf-8'))
        SendingId = getSendingID(request)
        if SendingId == -1:   
            Request_new = {}      
            Request_new['user_id'] = userId.pk
            Request_new['moder_id'] = random.choice(user.objects.filter(is_moder=True)).pk
            sendingserializer = sendingSerializer(data=Request_new)
            if sendingserializer.is_valid():
                sendingserializer.save()  
                SendingId = sendingserializer.data['id']
            else:
                return Response(sendingSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        link = {}
        link['Receiver'] = pk
        link['Sending'] = SendingId
        link['is_contact'] = False
        serializer = sendingReceiverSerializer(data=link)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        currentUser = user.objects.get(login=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moder:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try: 
            new_status = request.data['status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Receiver = get_object_or_404(receiver, pk=pk)
        Receiver.status = new_status
        Receiver.save()
        serializer = receiverSerializer(Receiver)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=receiverSerializer)
    def put(self, request, pk, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        currentUser = user.objects.get(login=session_storage.get(session_id).decode('utf-8'))
        if not currentUser.is_moder:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        product = get_object_or_404(receiver, pk=pk)
        fields = request.data.keys()
        if 'id' in fields or 'status' in fields or 'last_modified' in fields:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer = receiverSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            if 'image' in fields:
                putProductImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
