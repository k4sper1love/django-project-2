from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import StudentSerializer
from students.tasks import notify_student_profile_update
from core.logging import logger
from rest_framework.response import Response
from .permissions import IsAdminOrTeacher

CACHE_TTL = getattr(settings, 'CACHE_TTL', 300)

class StudentListView(ListCreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Student.objects.all()
        elif user.role == 'teacher':
            return Student.objects.filter(user__role='student')
        return Student.objects.none()

    @swagger_auto_schema(
        operation_summary="Get a list of students",
        operation_description="Returns a list of all students. The administrator sees everyone, the teacher sees only the students.",
        responses={200: StudentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info("Fetching student list")
        cached_students = cache.get('student_list')
        if cached_students and request.user.role == 'admin':
            logger.info("Student list fetched from cache")
            return Response(cached_students)
        students = self.get_queryset()
        serializer = self.get_serializer(students, many=True)
        if request.user.role == 'admin':
            cache.set('student_list', serializer.data, timeout=CACHE_TTL)
        logger.info("Student list fetched from database and cached")
        return Response(serializer.data)


class StudentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    @swagger_auto_schema(
        operation_summary="Update student data",
        operation_description="Updates the data of a specific student (available to the administrator and teacher).",
        request_body=StudentSerializer,
        responses={200: StudentSerializer}
    )
    def put(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        logger.info(f"Updating student {pk}")
        try:
            student = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(student, data=request.data)
            if serializer.is_valid():
                serializer.save()
                notify_student_profile_update.delay(student.user.email)
                cache.delete(f'student_{pk}')
                cache.set(f'student_{pk}', serializer.data, timeout=CACHE_TTL)
                logger.info(f"Student {pk} updated and cached")
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Student.DoesNotExist:
            logger.error(f"Student {pk} not found")
            return Response({"error": "Student not found"}, status=404)
