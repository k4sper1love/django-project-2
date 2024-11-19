from students.serializers import StudentSerializer
from courses.models import Course
from users.serializers import CustomUserSerializer
from rest_framework import serializers
from courses.models import Enrollment

class CourseSerializer(serializers.ModelSerializer):
    instructor = CustomUserSerializer()

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'instructor']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    course = CourseSerializer()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrollment_date']
        read_only_fields = ['enrollment_date']
