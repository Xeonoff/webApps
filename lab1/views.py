from django.shortcuts import render
from datetime import date
from django.http import HttpResponse
from .models import receiver
from django.db import connection

def getdata(request):
    data = receiver.objects.all()
    return render(request, 'recipients.html', {'data' : {
        'recipients': data
    }})

def GetPart(request, id):
    data = receiver.objects.get(pk = id)
    return render(request, 'recipient.html', {'data' : {
        'id': id,
        'recipients': data
    }})
def find(request):
    data = receiver.objects.all()
    try:
       input = request.GET['receiver']
    except:
        input = ''
    return render(request, 'recipients.html', {'data' : {
        'recipients' : receiver.objects.filter(full_name__startswith = input),
        'input' : input,
        }})

# Create your views here.
