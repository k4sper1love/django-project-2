from rest_framework import serializers
from analytics.models import APIRequestLog

class APIRequestLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = APIRequestLog
        fields = ['id', 'user', 'endpoint', 'method', 'timestamp', 'status_code']
        read_only_fields = ['timestamp']
