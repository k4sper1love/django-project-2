from django.urls import path
from .views import CourseListView, CourseDetailView, EnrollmentListView

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment-list'),
]
