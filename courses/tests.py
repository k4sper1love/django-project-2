import pytest
from rest_framework.test import APIClient
from users.models import User
from students.models import Student
from courses.models import Course

@pytest.mark.django_db
def test_teacher_create_course():
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="password123", role="teacher")
    client = APIClient()
    client.force_authenticate(user=teacher)

    response = client.post('/api/courses/', {
        "name": "Biology 101",
        "description": "Introduction to Biology",
    }, format='json')

    assert response.status_code == 201
    assert response.data['name'] == "Biology 101"


@pytest.mark.django_db
def test_student_cannot_create_course():
    student = User.objects.create_user(username="student", email="student@example.com", password="password123", role="student")
    client = APIClient()
    client.force_authenticate(user=student)

    response = client.post('/api/courses/', {"name": "Fake Course", "description": "Invalid"}, format='json')
    assert response.status_code == 403
    assert response.data['detail'] == "Only teachers can create courses."


@pytest.mark.django_db
def test_student_enroll_in_course():
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="password123", role="teacher")
    student_user = User.objects.create_user(username="student", email="student@example.com", password="password123", role="student")
    student = Student.objects.create(user=student_user)
    course = Course.objects.create(name="Physics 101", description="Intro Physics", instructor=teacher)

    client = APIClient()
    client.force_authenticate(user=student_user)

    response = client.post('/api/enrollments/', {"student": student.id, "course": course.id}, format='json')
    assert response.status_code == 201
    assert response.data['course'] == course.id
