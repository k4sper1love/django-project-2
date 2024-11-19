from rest_framework import serializers
from grades.models import Grade
from students.serializers import StudentSerializer
from courses.serializers import CourseSerializer
from users.serializers import CustomUserSerializer

class GradeSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    course = CourseSerializer()
    teacher = CustomUserSerializer()

    class Meta:
        model = Grade
        fields = ['id', 'student', 'course', 'grade', 'date', 'teacher']
        read_only_fields = ['date']
