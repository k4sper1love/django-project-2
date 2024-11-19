import pytest
from rest_framework.test import APIClient
from unittest.mock import patch
from grades.tasks import notify_student_about_new_grade
from users.models import User
from students.models import Student
from courses.models import Course

@pytest.mark.django_db
def test_teacher_add_grade():
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="password123", role="teacher")
    student_user = User.objects.create_user(username="student", email="student@example.com", password="password123", role="student")
    student = Student.objects.create(user=student_user)
    course = Course.objects.create(name="Physics", instructor=teacher)

    client = APIClient()
    client.force_authenticate(user=teacher)
    response = client.post('/api/grades/', {
        "student": student.id,
        "course": course.id,
        "grade": "B+",
        "comment": "Well done!"
    }, format='json')

    assert response.status_code == 201
    data = response.json()
    assert data['grade'] == "B+"
    assert data['comment'] == "Well done!"

@pytest.mark.django_db
def test_student_cannot_add_grade():
    student_user = User.objects.create_user(username="student", email="student@example.com", password="password123", role="student")

    client = APIClient()
    client.force_authenticate(user=student_user)
    response = client.post('/api/grades/', {
        "student": 1,
        "course": 1,
        "grade": "A"
    }, format='json')

    assert response.status_code == 403
    assert response.json()['error'] == "Only teachers can add grades"

@patch("grades.tasks.send_mail")
def test_notify_student_about_new_grade_task(mock_send_mail):
    notify_student_about_new_grade("student@example.com", "Math 101", "A")

    mock_send_mail.assert_called_once_with(
        'New Grade Assigned',
        'You have received a new grade in Math 101: A.',
        'admin@example.com',
        ['student@example.com'],
        fail_silently=False
    )
