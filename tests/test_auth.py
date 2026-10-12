import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:
    
    def test_user_registration(self, client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = client.post(url, data, content_type='application/json')
        
        assert response.status_code == 201
        assert 'username' in response.json()
        assert User.objects.filter(username='newuser').exists()
    
    def test_registration_password_mismatch(self, client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'wrongpass',
        }
        response = client.post(url, data, content_type='application/json')
        
        assert response.status_code == 400
    
    def test_user_login(self, client, user):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post(url, data, content_type='application/json')
        
        assert response.status_code == 200
        assert response.json()['username'] == 'testuser'
    
    def test_login_invalid_credentials(self, client):
        url = reverse('login')
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        response = client.post(url, data, content_type='application/json')
        
        assert response.status_code == 401
    
    def test_logout(self, authenticated_client):
        url = reverse('logout')
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
    
    def test_me_endpoint(self, authenticated_client, user):
        url = reverse('me')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.json()['username'] == user.username
    
    def test_me_endpoint_unauthorized(self, client):
        url = reverse('me')
        response = client.get(url)
        
        assert response.status_code == 403
