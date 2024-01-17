from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ..models import sending
import json
@csrf_exempt
@require_http_methods(["PUT"])
def update_sending_status(request):
    try:
        # Загрузить тело запроса и проверить пароль
        data = json.loads(request.body)
        if data.get('password') != 'abrakadabra':
            return HttpResponseForbidden('Invalid password.')
        
        # Проверить наличие статуса
        id_sending = data.get('id_sending')
        new_status = data.get('rand_status')
        if new_status is None:
            return HttpResponseBadRequest('Bad Request: Missing status field.')
        
       # Найти и обновить статус объекта Sending
        try:
            Sending = sending.objects.get(pk=id_sending)
            Sending.status_send = new_status
            Sending.save()
        except Sending.DoesNotExist:
            return HttpResponseBadRequest('Sending object not found.')

        # Успешный ответ с обновленным статусом
        return JsonResponse({'id_sending': id_sending, 'status': new_status})

    except (json.JSONDecodeError, KeyError):
        # В случае ошибки входных данных
        return HttpResponseBadRequest('Bad Request: Invalid JSON.')

