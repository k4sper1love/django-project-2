import pytest
from users.models import User
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("password123")
    assert user.role == "student"

@pytest.mark.django_db
def test_admin_user_creation():
    admin = User.objects.create_user(username="adminuser", email="admin@example.com", password="adminpass", role="admin")
    assert admin.role == "admin"


@pytest.mark.django_db
def test_user_list_as_admin():
    admin = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")
    User.objects.create_user(username="student1", email="student1@example.com", password="password123", role="student")
    User.objects.create_user(username="teacher1", email="teacher1@example.com", password="password456", role="teacher")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get('/api/users/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert any(user['role'] == 'admin' for user in data)
    assert any(user['role'] == 'student' for user in data)
    assert any(user['role'] == 'teacher' for user in data)


@pytest.mark.django_db
def test_user_list_as_teacher():
    # Создаём учителя и несколько пользователей
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="teacherpass",
                                       role="teacher")
    User.objects.create_user(username="student1", email="student1@example.com", password="password123", role="student")
    User.objects.create_user(username="student2", email="student2@example.com", password="password456", role="student")
    User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")

    client = APIClient()
    client.force_authenticate(user=teacher)
    response = client.get('/api/users/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(user['role'] == 'student' for user in data)

@pytest.mark.django_db
def test_user_list_as_admin():
    admin = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")
    User.objects.create_user(username="student1", email="student1@example.com", password="password123", role="student")
    User.objects.create_user(username="teacher1", email="teacher1@example.com", password="password456", role="teacher")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get('/api/users/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert any(user['role'] == 'admin' for user in data)
    assert any(user['role'] == 'student' for user in data)
    assert any(user['role'] == 'teacher' for user in data)


@pytest.mark.django_db
def test_user_list_as_teacher():
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="teacherpass",
                                       role="teacher")
    User.objects.create_user(username="student1", email="student1@example.com", password="password123", role="student")
    User.objects.create_user(username="student2", email="student2@example.com", password="password456", role="student")
    User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")

    client = APIClient()
    client.force_authenticate(user=teacher)
    response = client.get('/api/users/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(user['role'] == 'student' for user in data)


@pytest.mark.django_db
def test_user_list_as_student():
    student = User.objects.create_user(username="student", email="student@example.com", password="studentpass",
                                       role="student")
    User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")

    client = APIClient()
    client.force_authenticate(user=student)
    response = client.get('/api/users/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.django_db
def test_user_detail_as_admin():
    admin = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")
    student = User.objects.create_user(username="student1", email="student1@example.com", password="password123",
                                       role="student")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.get(f'/api/users/{student.id}/')

    assert response.status_code == 200
    data = response.json()
    assert data['username'] == "student1"
    assert data['email'] == "student1@example.com"
    assert data['role'] == "student"


@pytest.mark.django_db
def test_user_detail_as_teacher():
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="teacherpass",
                                       role="teacher")
    student = User.objects.create_user(username="student1", email="student1@example.com", password="password123",
                                       role="student")

    client = APIClient()
    client.force_authenticate(user=teacher)
    response = client.get(f'/api/users/{student.id}/')

    assert response.status_code == 200
    data = response.json()
    assert data['username'] == "student1"


@pytest.mark.django_db
def test_user_update_as_admin():
    admin = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")
    student = User.objects.create_user(username="student1", email="student1@example.com", password="password123",
                                       role="student")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.put(f'/api/users/{student.id}/', data={
        "username": "updatedstudent",
        "email": "updated@example.com",
        "role": "student"
    }, format='json')

    assert response.status_code == 200
    data = response.json()
    assert data['username'] == "updatedstudent"
    assert data['email'] == "updated@example.com"


@pytest.mark.django_db
def test_user_delete_as_admin():
    admin = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass", role="admin")
    student = User.objects.create_user(username="student1", email="student1@example.com", password="password123",
                                       role="student")

    client = APIClient()
    client.force_authenticate(user=admin)
    response = client.delete(f'/api/users/{student.id}/')

    assert response.status_code == 204
    assert not User.objects.filter(id=student.id).exists()


@pytest.mark.django_db
def test_user_delete_as_teacher():
    teacher = User.objects.create_user(username="teacher", email="teacher@example.com", password="teacherpass",
                                       role="teacher")
    student = User.objects.create_user(username="student1", email="student1@example.com", password="password123",
                                       role="student")

    client = APIClient()
    client.force_authenticate(user=teacher)
    response = client.delete(f'/api/users/{student.id}/')

    assert response.status_code == 403
