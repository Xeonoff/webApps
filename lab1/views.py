from django.shortcuts import render
from .models import Card

def getdata():
    return {
        'data' : {
            'recipients' : [
                {'title' : 'Ктотов Ктототам Ктототамович', 'BDate' : '17.09.1992', 'sex' : 'm', 'email' : 'sanitar1992@gmail.com', 'available mem' : '100', 'img' : 'images/1012.jpg', 'id' : 1},
                {'title' : 'Недопонятый гений', 'BDate' : '11.11.2001', 'sex' : 'f', 'email' : 'paracetamol2001@gmail.com', 'available mem' : '100', 'img' : 'images/rec2316.jpg', 'id' : 2},
                {'title' : 'Какой-то мужик', 'BDate' : '12.12.2002', 'sex' : 'm', 'email' : 'paralon2002@gmail.com', 'available mem' : '100', 'img' : 'images/recbogdan.jpg', 'id' : 3},
                {'title' : 'Перега Сират', 'BDate': '21.04.1999', 'sex' : 'm', 'email' : 'eshkere1448@gmail.com', 'available mem' : '100', 'img' : 'images/recpirat.jpg', 'id' : 4},
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
    res = {'data' : {'recipients' : []}}
    try:
       input = request.GET['search']
    except:
        input = '' 
    for recipient in data['data']['recipients']:
        if str(recipient['title']).lower().find(input.lower()) != -1:
            res['data']['recipients'].append(recipient)
    return render(request, 'recipients.html', res)
# Create your views here.
