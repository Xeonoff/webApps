from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from datetime import datetime
from .getUserId import *
from ..minio.minioClass import MinioClass
from ..filters import *
def getInputtingId():
    requestlist = sending.objects.filter(user_id = getUserId()).filter(status = 'I')
    if not requestlist.exists():
        return -1
    else:
        return requestlist[0].pk
def checkStatusUpdate(old, new, isModer):
    return ((not isModer) and (new in ['P', 'D']) and (old == 'I')) or (isModer and (new in ['A', 'W']) and (old == 'P'))

def getReceiverInSendingWithImage(serializer: receiverSerializer):
    minio = MinioClass()
    receiverData = serializer.data
    receiverData['img'] = minio.getImage('images', serializer.data['id'])
    return receiverData

# добавляет данные продукта ко всем позициям заказа
def getSendingPositionsWithReceiverData(serializer: PositionSerializer):
    positions = []
    for item in serializer.data:
        Receiver = get_object_or_404(receiver, pk=item['Receiver'])
        positionData = item
        positionData['receiver_data'] = getReceiverInSendingWithImage(receiverSerializer(Receiver))
        positions.append(positionData)
    return positions

@api_view(['Get', 'Put', 'Delete'])
def process_SendingList(request, format=None):

    # получение списка заказов
    if request.method == 'GET':
        application = filterSending(sending.objects.all(), request)
        serializer = sendingSerializer(application, many=True)
        wideApplication = serializer.data
        for i, wa in enumerate(serializer.data):
            User = get_object_or_404(user, pk=wa['user_id'])
            Moder = get_object_or_404(user, pk=wa['moder_id'])
            wideApplication[i]['user_name'] = User.name
            wideApplication[i]['moder_name'] = Moder.name
        return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
    
    # отправка заказа пользователем
    elif request.method == 'PUT':
        application = get_object_or_404(sending, pk=getInputtingId())
        new_status = "P"
        if checkStatusUpdate(application.status, new_status, isModer=False):
            application.status = new_status
            application.sent = datetime.now()
            application.save()
            serializer = sendingSerializer(application)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление заказа пользователем
    elif request.method == 'DELETE':
        new_status = "D"
        application = get_object_or_404(sending, pk=getInputtingId())
        if checkStatusUpdate(application.status, new_status, isModer=False):
            application.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['Get', 'Put'])
def process_sending_detail(request, pk, format=None):

    # получение заказа
    if request.method == 'GET':
        application = get_object_or_404(sending, pk=pk)
        applicationSerializer = sendingSerializer(application)

        positions = sendingReceiver.objects.filter(Sending=pk)
        positionsSerializer = PositionSerializer(positions, many=True)

        response = applicationSerializer.data
        response['positions'] = getSendingPositionsWithReceiverData(positionsSerializer)

        return Response(response, status=status.HTTP_202_ACCEPTED)
    
     # перевод заказа модератором на статус A или W
    elif request.method == 'PUT':
        application = get_object_or_404(sending, pk=pk)
        try: 
            new_status = request.data['status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if checkStatusUpdate(application.status, new_status, isModer=True):
            application.status = new_status
            application.received = None
            application.save()
            wideApplication = sendingSerializer(application).data
            wideApplication['user_name'] = user.objects.get(pk = wideApplication['user_id']).name
            wideApplication['moder_name'] = user.objects.get(pk = wideApplication['moder_id']).name
            return Response(wideApplication, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
   
        