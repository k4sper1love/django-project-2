from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.conf import settings
from .models import Course, Student, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from courses.tasks import notify_students_about_new_course
from core.logging import logger

CACHE_TTL = getattr(settings, 'CACHE_TTL', 300)


class CourseListView(ListCreateAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get a list of courses",
        operation_description="Returns a list of active courses for students",
        responses={200: CourseSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"Fetching course list by {request.user.username}")
        cached_courses = cache.get('course_list')
        if cached_courses:
            logger.info("Course list fetched from cache")
            return Response(cached_courses)

        courses = self.get_queryset()
        serializer = self.get_serializer(courses, many=True)
        cache.set('course_list', serializer.data, timeout=CACHE_TTL)
        logger.info("Course list fetched from database and cached")
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Add a course",
        operation_description="Creates a new course (teachers only)",
        request_body=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def post(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied("Only teachers can create courses.")

        logger.info(f"Teacher {request.user.username} is creating a course")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            course = serializer.save(instructor=request.user)
            student_emails = [student.user.email for student in Student.objects.all()]
            notify_students_about_new_course.delay(course.name, student_emails)
            logger.info(f"Course '{course.name}' created and notifications sent")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change course",
        operation_description="Allows the teacher to change the course",
        request_body=CourseSerializer,
        responses={200: CourseSerializer}
    )
    def put(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied("Only teachers can update courses.")

        pk = kwargs.get("pk")
        logger.info(f"Updating course {pk} by {request.user.username}")
        try:
            course = self.get_queryset().get(pk=pk)
            if course.instructor != request.user:
                raise PermissionDenied("You can only modify your own courses.")

            serializer = self.get_serializer(course, data=request.data)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'course_{pk}')
                cache.set(f'course_{pk}', serializer.data, timeout=CACHE_TTL)
                logger.info(f"Course {pk} updated and cached")
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except Course.DoesNotExist:
            logger.error(f"Course {pk} not found")
            return Response({"error": "Course not found"}, status=404)


class EnrollmentListView(ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Sign up for a course",
        operation_description="Allows students to enroll in courses",
        request_body=EnrollmentSerializer,
        responses={201: EnrollmentSerializer}
    )
    def post(self, request, *args, **kwargs):
        if request.user.role != 'student':
            raise PermissionDenied("Only students can enroll in courses.")

        logger.info(f"Student {request.user.username} enrolling in a course")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            enrollment = serializer.save()
            logger.info(f"Student {enrollment.student.user.username} enrolled in {enrollment.course.name}")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
