from receivers_selection_api.models import receiver, user, sending, sendingReceiver
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from collections import OrderedDict

class receiverSerializer(serializers.ModelSerializer):
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields
    class Meta:
        model = receiver
        fields = '__all__'

class userSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    is_staff = serializers.BooleanField(default=False, required=False)
    is_moder = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    is_active = serializers.BooleanField(default=True, required=False)
    class Meta:
        model = user
        fields = '__all__'

class UserLoginSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class sendingSerializer(serializers.ModelSerializer):
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields
    class Meta:
        model = sending
        fields = '__all__'

class sendingReceiverSerializer(serializers.ModelSerializer):
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields
    class Meta:
        model = sendingReceiver
        fields = '__all__'

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = sendingReceiver
        fields = ["is_contact","Receiver"]