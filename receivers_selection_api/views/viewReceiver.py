from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from random import *
from receivers_selection_api.serializers import *
from receivers_selection_api.models import *
from rest_framework.views import APIView
from .getUserId import *
from rest_framework.decorators import api_view
from ..minio.minioClass import MinioClass
from ..filters import *

def getInputId():
    requestlist = sending.objects.filter(user_id = getUserId()).filter(status = 'I')
    if not requestlist.exists():
        return -1
    else:
        return requestlist[0].pk
    
def getProductDataWithImage(serializer: receiverSerializer):
    minio = MinioClass()
    receiverData = serializer.data
    receiverData.update({'img': minio.getImage('images', serializer.data['id'])})
    return receiverData

def postProductImage(request, serializer: receiverSerializer):
    minio = MinioClass()
    minio.addImage('images', serializer.data['id'], request.data['image'])

def putProductImage(request, serializer: receiverSerializer):
    minio = MinioClass()
    minio.removeImage('images', serializer.data['id'])
    minio.addImage('images', serializer.data['id'], request.data['image'])

@api_view(['Get', 'Post'])
def process_Receiverlist(request, format=None):
    if request.method == 'GET':
        sendingid = getInputId()
        List = {
            'SendingId' : sendingid
        }
        Receivers = filterReceiver(receiver.objects.all(), request)
        ReceiversData = [getProductDataWithImage(receiverSerializer(Receiver)) for Receiver in Receivers]
        List ['Receivers'] = ReceiversData
        return Response(List, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'POST':
        serializer = receiverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postProductImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get', 'Post', 'Put', 'Delete'])
def procces_receiver_detail(request, pk, format=None):
    if request.method == 'GET':
        Receiver = get_object_or_404(receiver,pk=pk)
        serializer = receiverSerializer(Receiver)
        return Response(getProductDataWithImage(serializer), status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'POST': 
        userId = getUserId()
        SendingId = getInputId()
        if SendingId == -1:   
            Request_new = {}      
            Request_new['user'] = userId
            Request_new['moderator'] = random.choice(user.objects.filter(is_moderator=True)).pk
            sendingserializer = sendingSerializer(data=sending)
            if sendingserializer.is_valid():
                sendingserializer.save()  
                SendingId = sendingserializer.data['id']
            else:
                return Response(sendingSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        link = {}
        link['Receiver'] = pk
        link['Sending'] = SendingId
        link['is_contact'] = False
        serializer = sendingReceiver(data=link)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try: 
            new_status = request.data['status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Receiver = get_object_or_404(receiver, pk=pk)
        Receiver.status = new_status
        Receiver.save()
        serializer = receiverSerializer(Receiver)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'PUT':
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
