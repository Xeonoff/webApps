from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

import redis
from receivers_api.settings import REDIS_HOST, REDIS_PORT

from ..services import *


session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

class process_MM(APIView):
    @swagger_auto_schema(request_body=sendingReceiverSerializer)
    def put(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try: 
            cnt = request.data['Reciver_count']
            productId = request.data['Receiver']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if receiver.objects.get(pk=productId).cnt < cnt:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        links = sendingReceiver.objects.filter(Receiver=productId).filter(Sending=getSendingID(request))
        if len(links) > 0:
            links[0].Reciver_count = cnt
            links[0].save()
            return Response(PositionSerializer(links[0]).data, status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление продукта из заказа
    @swagger_auto_schema(request_body=sendingReceiverSerializer)
    def delete(self, request, format=None):
        session_id = get_session(request)
        if session_id is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try: 
            productId = request.data['Receiver']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        sendingID = getSendingID()
        links = sendingReceiver.objects.filter(Receiver=productId).filter(Sending=sendingID)
        if len(links) > 0:
            links[0].delete()
            if len(sendingReceiver.objects.filter(Sending=sendingID)) == 0:
                sending.objects.get(pk=sendingID).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)