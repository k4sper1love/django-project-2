from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.conf import settings
from .models import Attendance
from .serializers import AttendanceSerializer
from attendance.tasks import notify_student_about_absence
from core.logging import logger

CACHE_TTL = getattr(settings, 'CACHE_TTL', 300)

class AttendanceListView(ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'teacher':
            return Attendance.objects.filter(course__instructor=self.request.user)
        elif self.request.user.role == 'student':
            return Attendance.objects.filter(student__user=self.request.user)
        else:
            raise PermissionDenied("Only teachers and students can view attendance records.")

    @swagger_auto_schema(
        operation_summary="Get the attendance list",
        operation_description="Returns a list of attendance for students or teacher courses",
        responses={200: AttendanceSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info(f"Fetching attendance list for {request.user.username}")
        cache_key = f'attendance_list_{request.user.id}'
        cached_attendance = cache.get(cache_key)
        if cached_attendance:
            logger.info("Attendance list fetched from cache")
            return Response(cached_attendance)

        attendance = self.get_queryset()
        serializer = self.get_serializer(attendance, many=True)
        cache.set(cache_key, serializer.data, timeout=CACHE_TTL)
        logger.info("Attendance list fetched from database and cached")
        return Response(serializer.data)


class AttendanceCreateView(CreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Add an attendance record",
        operation_description="Adds a new student attendance record (teachers only)",
        request_body=AttendanceSerializer,
        responses={201: AttendanceSerializer}
    )
    def post(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied("Only teachers can add attendance records.")

        logger.info(f"Adding new attendance record by {request.user.username}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            attendance = serializer.save()
            if not attendance.status:
                notify_student_about_absence.delay(
                    attendance.student.user.email,
                    attendance.course.name
                )
                logger.info(f"Notification sent for absent student {attendance.student.user.email}")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AttendanceDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        attendance = super().get_object()
        if self.request.user.role == 'teacher' and attendance.course.instructor != self.request.user:
            raise PermissionDenied("You can only manage attendance records for your own courses.")
        if self.request.user.role == 'student' and attendance.student.user != self.request.user:
            raise PermissionDenied("You can only view your own attendance records.")
        return attendance

    @swagger_auto_schema(
        operation_summary="Update the attendance record",
        operation_description="Updates the data of a specific attendance record (teachers only)",
        request_body=AttendanceSerializer,
        responses={200: AttendanceSerializer}
    )
    def put(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied("Only teachers can update attendance records.")

        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete the attendance record",
        operation_description="Deletes a specific attendance record (teachers only)",
        responses={204: "The attendance record has been successfully deleted"}
    )
    def delete(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied("Only teachers can delete attendance records.")

        return super().delete(request, *args, **kwargs)
