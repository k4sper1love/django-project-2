from rest_framework import serializers
from notifications.models import Notification
from users.serializers import CustomUserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'read']
        read_only_fields = ['created_at']
