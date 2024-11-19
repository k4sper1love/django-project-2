import pytest
from rest_framework.test import APIClient
from unittest.mock import patch
from notifications.models import Notification
from users.models import User
from notifications.tasks import create_course_notification


@pytest.mark.django_db
def test_create_notification():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    notification = Notification.objects.create(user=user, message="This is a test notification")
    assert notification.user == user
    assert notification.message == "This is a test notification"
    assert not notification.read


@pytest.mark.django_db
def test_notification_list_api():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    Notification.objects.create(user=user, message="Notification 1")
    Notification.objects.create(user=user, message="Notification 2")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/notifications/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['message'] == "Notification 1"


@pytest.mark.django_db
def test_update_notification():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    notification = Notification.objects.create(user=user, message="Test notification", read=False)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.put(f'/api/notifications/{notification.id}/', {"read": True}, format='json')

    assert response.status_code == 200
    notification.refresh_from_db()
    assert notification.read is True


@pytest.mark.django_db
def test_delete_notification():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    notification = Notification.objects.create(user=user, message="Test notification")

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.delete(f'/api/notifications/{notification.id}/')

    assert response.status_code == 204
    assert Notification.objects.count() == 0


@patch("notifications.tasks.Notification.objects.create")
def test_create_course_notification_task(mock_create):
    user1 = User.objects.create_user(username="user1", email="user1@example.com", password="password123")
    user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password456")

    user_ids = [user1.id, user2.id]
    create_course_notification("Python Course", user_ids)

    assert mock_create.call_count == 2
    assert mock_create.called
