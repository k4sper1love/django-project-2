from unittest.mock import patch
import pytest
from rest_framework.test import APIClient
from students.tasks import notify_student_profile_update
from users.models import User
from students.models import Student

@pytest.mark.django_db
def test_student_creation():
    user = User.objects.create_user(username="studentuser", email="student@example.com", password="password123", role="student")
    student = Student.objects.create(user=user, dob="2000-01-01")
    assert student.user.username == "studentuser"
    assert student.dob == "2000-01-01"

@pytest.mark.django_db
def test_student_list_as_admin():
    admin = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")
    user1 = User.objects.create_user(username="student1", email="student1@example.com", password="password123", role="student")
    Student.objects.create(user=user1, dob="2000-01-01")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get('/api/students/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

@pytest.mark.django_db
def test_student_list_as_teacher():
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="teacherpass", role="teacher")
    user1 = User.objects.create_user(username="student1", email="student1@example.com", password="password123", role="student")
    user2 = User.objects.create_user(username="student2", email="student2@example.com", password="password456", role="student")
    Student.objects.create(user=user1, dob="2000-01-01")
    Student.objects.create(user=user2, dob="2001-01-01")

    client = APIClient()
    client.force_authenticate(user=teacher)
    response = client.get('/api/students/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@patch("students.tasks.send_mail")
def test_notify_student_profile_update(mock_send_mail):
    student_email = "student@example.com"
    notify_student_profile_update(student_email)
    mock_send_mail.assert_called_once_with(
        'Profile Updated',
        'Your student profile has been updated.',
        'admin@example.com',
        [student_email],
        fail_silently=False
    )
