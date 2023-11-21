from receivers_selection_api.models import receiver, user, sending, sendingReceiver
from rest_framework import serializers


class receiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = receiver
        fields = '__all__'

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = '__all__'

class sendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = sending
        fields = '__all__'

class sendingReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = sendingReceiver
        fields = '__all__'

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = sendingReceiver
        fields = ["is_contact","Receiver"]