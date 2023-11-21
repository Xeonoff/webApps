from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(receiver)
admin.site.register(user)
admin.site.register(sending)
admin.site.register(sendingReceiver)