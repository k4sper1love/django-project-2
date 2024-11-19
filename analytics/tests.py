import pytest
from rest_framework.test import APIClient
from analytics.models import APIRequestLog
from users.models import User

@pytest.mark.django_db
def test_analytics_view():
    user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
    APIRequestLog.objects.create(user=user, endpoint="/api/test1/", method="GET", status_code=200)
    APIRequestLog.objects.create(user=user, endpoint="/api/test1/", method="POST", status_code=201)
    APIRequestLog.objects.create(user=user, endpoint="/api/test2/", method="GET", status_code=404)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get('/api/analytics/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['endpoint'] == "/api/test1/"
    assert data[0]['request_count'] == 2


@pytest.mark.django_db
def test_analytics_view_with_filters():
    user1 = User.objects.create_user(username="user1", email="user1@example.com", password="password123")
    user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password456")

    APIRequestLog.objects.create(user=user1, endpoint="/api/test1/", method="GET", status_code=200)
    APIRequestLog.objects.create(user=user2, endpoint="/api/test1/", method="GET", status_code=200)
    APIRequestLog.objects.create(user=user1, endpoint="/api/test2/", method="POST", status_code=201)

    client = APIClient()
    client.force_authenticate(user=user1)

    response = client.get('/api/analytics/', {"user_id": user1.id})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    response = client.get('/api/analytics/', {"method": "POST"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['endpoint'] == "/api/test2/"
