import pytest
from rest_framework.test import APIClient
from users.models import User
from students.models import Student
from courses.models import Course
from attendance.models import Attendance

@pytest.mark.django_db
def test_teacher_can_add_attendance():
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="password123", role="teacher")
    student_user = User.objects.create_user(username="student", email="student@example.com", password="password123", role="student")
    student = Student.objects.create(user=student_user)
    course = Course.objects.create(name="Math 101", instructor=teacher)

    client = APIClient()
    client.force_authenticate(user=teacher)
    response = client.post('/api/attendance/', {"student": student.id, "course": course.id, "status": True})

    assert response.status_code == 201
    assert response.data['status'] is True


@pytest.mark.django_db
def test_student_cannot_add_attendance():
    student_user = User.objects.create_user(username="student", email="student@example.com", password="password123", role="student")
    student = Student.objects.create(user=student_user)
    course = Course.objects.create(name="Math 101", instructor=User.objects.create_user(username="teacher", role="teacher"))

    client = APIClient()
    client.force_authenticate(user=student_user)
    response = client.post('/api/attendance/', {"student": student.id, "course": course.id, "status": True})

    assert response.status_code == 403
    assert response.data['detail'] == "Only teachers can add attendance records."


@pytest.mark.django_db
def test_student_can_view_their_own_attendance():
    student_user = User.objects.create_user(username="student", email="student@example.com", password="password123", role="student")
    student = Student.objects.create(user=student_user)
    course = Course.objects.create(name="Math 101", instructor=User.objects.create_user(username="teacher", role="teacher"))
    Attendance.objects.create(student=student, course=course, status=True)

    client = APIClient()
    client.force_authenticate(user=student_user)
    response = client.get('/api/attendance/')

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['status'] is True
