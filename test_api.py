"""
Quick API test script for manual testing.
Run after: python manage.py runserver
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_registration():
    """Test user registration."""
    response = requests.post(f"{BASE_URL}/auth/register/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    })
    print(f"Registration: {response.status_code}")
    if response.ok:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    return response

def test_login():
    """Test user login."""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/auth/login/", json={
        "username": "testuser",
        "password": "testpass123"
    })
    print(f"Login: {response.status_code}")
    if response.ok:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    return session

def test_me(session):
    """Test current user endpoint."""
    response = session.get(f"{BASE_URL}/auth/me/")
    print(f"Me: {response.status_code}")
    if response.ok:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")

def test_logout(session):
    """Test logout."""
    response = session.post(f"{BASE_URL}/auth/logout/")
    print(f"Logout: {response.status_code}")
    if response.ok:
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("=== Testing Authentication API ===\n")
    
    print("1. Testing registration...")
    test_registration()
    print()
    
    print("2. Testing login...")
    session = test_login()
    print()
    
    print("3. Testing /me endpoint...")
    test_me(session)
    print()
    
    print("4. Testing logout...")
    test_logout(session)
    print()
    
    print("=== Tests Complete ===")
