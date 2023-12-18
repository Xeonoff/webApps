from .models import *
import redis
from receivers_api.settings import REDIS_HOST, REDIS_PORT


session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


def get_session(request):
    ssid = request.COOKIES.get("session_id")
    if ssid is None:
        ssid = request.headers.get("authorization")
    return ssid


def getSendingID(request):
    session_id = get_session(request)
    if session_id is None:
        return -1

    User = user.objects.get(login=session_storage.get(session_id).decode('utf-8'))
    sendings = sending.objects.filter(user_id=User).filter(status='I')
    if sendings.exists():
        return sendings.first().pk
    return -1