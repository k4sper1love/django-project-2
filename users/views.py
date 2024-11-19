from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.conf import settings
from .models import User
from .serializers import CustomUserSerializer
from .permissions import IsAdmin, IsTeacher
from core.logging import logger
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

CACHE_TTL = getattr(settings, 'CACHE_TTL', 300)


class UserListView(ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        elif user.role == 'teacher':
            return User.objects.filter(role='student')
        return User.objects.none()

    @swagger_auto_schema(
        operation_summary="Get a list of users",
        operation_description="The administrator sees all users, the teacher sees only students",
        responses={200: CustomUserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        logger.info("Fetching user list")
        cached_users = cache.get('user_list')
        if cached_users and request.user.role == 'admin':
            logger.info("User list fetched from cache")
            return Response(cached_users)
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        if request.user.role == 'admin':
            cache.set('user_list', serializer.data, timeout=CACHE_TTL)
        logger.info("User list fetched from database and cached")
        return Response(serializer.data)


class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAuthenticated(), IsAdmin()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="Get user data",
        operation_description="Returns the data of a specific user by ID",
        responses={200: CustomUserSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        logger.info(f"Fetching user {pk}")
        cached_user = cache.get(f'user_{pk}')
        if cached_user:
            logger.info("User fetched from cache")
            return Response(cached_user)
        try:
            user = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(user)
            cache.set(f'user_{pk}', serializer.data, timeout=CACHE_TTL)
            logger.info("User fetched from database and cached")
            return Response(serializer.data)
        except User.DoesNotExist:
            logger.error(f"User {pk} not found")
            return Response({"error": "User not found"}, status=404)

    @swagger_auto_schema(
        operation_summary="Update user data",
        operation_description="Updates the data of a specific user by ID (administrator only)",
        request_body=CustomUserSerializer,
        responses={200: CustomUserSerializer}
    )
    def update(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        logger.info(f"Updating user {pk}")
        try:
            user = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'user_{pk}')
                cache.set(f'user_{pk}', serializer.data, timeout=CACHE_TTL)
                logger.info(f"User {pk} updated and cached")
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        except User.DoesNotExist:
            logger.error(f"User {pk} not found")
            return Response({"error": "User not found"}, status=404)

    @swagger_auto_schema(
        operation_summary="Delete user",
        operation_description="Removes a user from the system by ID (administrator only)",
        responses={204: "User successfully deleted"}
    )
    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        logger.info(f"Deleting user {pk}")
        try:
            user = self.get_queryset().get(pk=pk)
            user.delete()
            cache.delete(f'user_{pk}')
            cache.delete('user_list')
            logger.info(f"User {pk} deleted")
            return Response({"message": "User deleted successfully"}, status=204)
        except User.DoesNotExist:
            logger.error(f"User {pk} not found")
            return Response({"error": "User not found"}, status=404)
