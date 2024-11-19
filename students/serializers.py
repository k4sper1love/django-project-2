from rest_framework import serializers
from students.models import Student
from users.serializers import CustomUserSerializer

class StudentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'dob', 'registration_date']
        read_only_fields = ['registration_date']
