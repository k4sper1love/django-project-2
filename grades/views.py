from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.conf import settings
from .models import Grade
from .serializers import GradeSerializer
from grades.tasks import notify_student_about_new_grade
from core.logging import logger

CACHE_TTL = getattr(settings, 'CACHE_TTL', 300)

class GradeListView(ListCreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get a list of grades",
        responses={200: GradeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info("Fetching grade list")
        cached_grades = cache.get('grade_list')
        if cached_grades:
            logger.info("Grade list fetched from cache")
            return Response(cached_grades)
        grades = self.get_queryset()
        serializer = self.get_serializer(grades, many=True)
        cache.set('grade_list', serializer.data, timeout=CACHE_TTL)
        logger.info("Grade list fetched from database and cached")
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Add a grade",
        request_body=GradeSerializer,
        responses={201: GradeSerializer}
    )
    def post(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            logger.error(f"User {request.user.id} is not authorized to add grades")
            return Response({"error": "Only teachers can add grades"}, status=403)

        logger.info("Adding new grade")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            grade = serializer.save(teacher=request.user)
            notify_student_about_new_grade.delay(
                grade.student.user.email,
                grade.course.name,
                grade.grade
            )
            logger.info(f"Grade '{grade.grade}' added for student {grade.student.user.email}")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class GradeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update grade data",
        request_body=GradeSerializer,
        responses={200: GradeSerializer}
    )
    def put(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            logger.error(f"User {request.user.id} is not authorized to update grades")
            return Response({"error": "Only teachers can update grades"}, status=403)

        pk = kwargs.get("pk")
        logger.info(f"Updating grade {pk}")
        try:
            grade = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(grade, data=request.data)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'grade_{pk}')
                cache.set(f'grade_{pk}', serializer.data, timeout=CACHE_TTL)
                logger.info(f"Grade {pk} updated and cached")
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Grade.DoesNotExist:
            logger.error(f"Grade {pk} not found")
            return Response({"error": "Grade not found"}, status=404)
