from django.shortcuts import render, redirect
from .models import Card

def getdata():
    return {
        'data' : {
            'recipients' : [
                {'title' : 'Анна Ним', 'BDate' : '17.09.1992', 'sex' : 'f', 'email' : 'sanitar1992@gmail.com', 'available_mem' : '100', 'phone' : '+7(915)455-41-51', 'img' : 'images/1012.jpg', 'id' : 1},
                {'title' : 'Николай Теслин', 'BDate' : '11.11.1975', 'sex' : 'm', 'email' : 'paracetamol2001@gmail.com', 'available_mem' : '100', 'phone' : '+7(915)552-63-97', 'img' : 'images/rec2316.jpg', 'id' : 2},
                {'title' : 'Александр Фролов', 'BDate' : '12.12.1980', 'sex' : 'm', 'email' : 'paralon2002@gmail.com', 'available_mem' : '100', 'phone' : '+7(915)798-68-85', 'img' : 'images/recbogdan.jpg', 'id' : 3},
                {'title' : 'Сергей Пиратенко', 'BDate': '21.04.1999', 'sex' : 'm', 'email' : 'seregapirat1448@gmail.com', 'available_mem' : '100', 'phone' : '+7(915)210-21-88', 'img' : 'images/recpirat.jpg', 'id' : 4},
            ]
        }
    }
data = getdata()

def GetParts(request):
    return render(request, 'recipients.html', data)

def GetPart(request, id):
    data = getdata()
    result = {}
    for recipient in data['data']['recipients']:
        if recipient['id'] == id:
            result = recipient
    return render(request, 'recipient.html', {'data' : {
        'id': id,
        'recipients': result
    }})
def find(request):
    data = getdata()
    res = []
    try:
       input = request.GET['recipient_sch']
    except:
        input = '' 
    for recipient in data['data']['recipients']:
        if str(recipient['title']).lower().find(input.lower()) != -1:
            res.append(recipient)
    return render(request, 'recipients.html', {'data' : {
        'input': input,
        'recipients': res
    }})
# Create your views here.
