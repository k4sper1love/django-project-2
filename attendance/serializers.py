from rest_framework import serializers
from attendance.models import Attendance
from students.serializers import StudentSerializer
from courses.serializers import CourseSerializer

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    course = CourseSerializer()
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'course', 'date', 'status', 'status_label']
        read_only_fields = ['date']

    def get_status_label(self, obj):
        return "Present" if obj.status else "Absent"
