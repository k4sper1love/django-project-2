from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from .models import User

class CustomUserCreateSerializer(UserCreateSerializer):
    def create(self, validated_data):
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email'].split('@')[0]
        return super().create(validated_data)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'role')

class CustomUserSerializer(UserSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'role', 'role_display')