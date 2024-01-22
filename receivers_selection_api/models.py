from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager

class NewUserManager(UserManager):
    def create_user(self, username, password, **extra_fields):
        User: user = self.model(username=username, **extra_fields)
        User.set_password(password)
        User.save()
        return User

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_moder', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)
    
class receiver(models.Model):
    full_name = models.CharField(max_length=50, verbose_name="ФИО")
    status = models.CharField(max_length=1, verbose_name="Статус отображения", default="1")
    bdate = models.DateField(verbose_name="Дата рождения")
    sex = models.CharField(max_length=1, verbose_name="Пол")
    email = models.CharField(max_length=50, verbose_name="Эл. почта")
    available_mem = models.FloatField(verbose_name="Память на хранение", default=102400)
    phone = models.CharField(max_length=20, verbose_name="Тел. номер")
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Последнее изменение", null=True, blank=True)

    
class user(AbstractBaseUser, PermissionsMixin):
    objects = NewUserManager()
    username = models.CharField(max_length=32, verbose_name="Логин", unique=True)
    password = models.CharField(max_length=256, verbose_name="Пароль")
    is_moder = models.BooleanField(default=False, verbose_name="Модератор")
    is_staff = models.BooleanField(verbose_name="Админ", default=False)
    is_superuser = models.BooleanField(verbose_name="Все права", default=False)
    is_active = models.BooleanField(verbose_name="Активный", default=True)
    USERNAME_FIELD = 'username'
    
    def __str__(self):
        return self.username

class sending(models.Model):
    created = models.DateTimeField(auto_now=True, verbose_name="Создано")
    sent = models.DateTimeField(verbose_name="Отправлен", null = True, blank=True)
    received = models.DateTimeField(verbose_name="Получен", null = True, blank = True)
    status = models.CharField(max_length=20, verbose_name="Статус", default='I') # I - inputing, P - processing, D - deleted by user, A - success, W - fail
    status_send = models.CharField(max_length=20, verbose_name="Статус отправки", default='Q')# Q - in queue, A - accepted, D - delivered, R - received
    user_name = models.ForeignKey(user, on_delete = models.CASCADE, verbose_name="ID_Пользователь", related_name='user_name')
    moder_name = models.ForeignKey(user, on_delete = models.CASCADE, verbose_name="ID_Модератор", related_name='moder_name', null = True)

class sendingReceiver(models.Model):
    is_contact = models.BooleanField(verbose_name="ваш контакт?", default=False)
    Reciver_count = models.IntegerField(verbose_name="Количество получателей в данном запросе", default = 0)
    Receiver = models.ForeignKey(receiver, on_delete = models.CASCADE, verbose_name="Получатель")
    Sending = models.ForeignKey(sending, on_delete = models.CASCADE, verbose_name="Отправка файла")
    class Meta:
        unique_together = (('Receiver', 'Sending'),)
# Create your models here.

# Create your models here.
