from django.db import models
class receiver(models.Model):
    full_name = models.CharField(max_length=50, verbose_name="ФИО")
    img = models.CharField(max_length=100, verbose_name="Изображение", null=True, blank=True)
    status = models.CharField(max_length=1, verbose_name="Статус отображения", default="1")
    bdate = models.DateField(verbose_name="Дата рождения")
    sex = models.CharField(max_length=1, verbose_name="Пол")
    email = models.CharField(max_length=50, verbose_name="Эл. почта")
    available_mem = models.FloatField(verbose_name="Память на хранение", default=102400)
    phone = models.CharField(max_length=20, verbose_name="Тел. номер")
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Последнее изменение", null=True, blank=True)

    
class user(models.Model):
    name = models.CharField(max_length=20, verbose_name="Имя")
    login = models.CharField(max_length=20, verbose_name="Логин")
    password = models.CharField(max_length=20, verbose_name="Пароль")
    is_moder = models.BooleanField(default=False, verbose_name="Модератор")

class sending(models.Model):
    created = models.DateTimeField(auto_now=True, verbose_name="Создано")
    sent = models.DateTimeField(verbose_name="Отправлен", null = True, blank=True)
    received = models.DateTimeField(verbose_name="Получен", null = True, blank = True)
    status = models.CharField(max_length=20, verbose_name="Статус", default='I') # I - inputing, P - processing, D - deleted by user, A - success, W - fail
    user_id = models.ForeignKey(user, on_delete = models.CASCADE, verbose_name="ID_Пользователь", related_name='user_id')
    moder_id = models.ForeignKey(user, on_delete = models.CASCADE, verbose_name="ID_Модератор", related_name='moder_id')

class sendingReceiver(models.Model):
    is_contact = models.BooleanField(verbose_name="ваш контакт?", default=False)
    Reciver_count = models.IntegerField(verbose_name="Количество получателей в данном запросе", default = 0)
    Receiver = models.ForeignKey(receiver, on_delete = models.CASCADE, verbose_name="Получатель")
    Sending = models.ForeignKey(sending, on_delete = models.CASCADE, verbose_name="Отправка файла")
    class Meta:
        unique_together = (('Receiver', 'Sending'),)
# Create your models here.

# Create your models here.
