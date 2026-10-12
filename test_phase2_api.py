"""
Phase 2 API test script for manual testing.
Run after: python manage.py runserver
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
session = requests.Session()


def login():
    """Login and return session."""
    response = session.post(f"{BASE_URL}/auth/login/", json={
        "username": "testuser",
        "password": "testpass123"
    })
    print(f"Login: {response.status_code}")
    return response.ok


def test_roles():
    """Test role endpoints."""
    print("\n=== Testing Roles ===")
    
    # Create role
    response = session.post(f"{BASE_URL}/roles/", json={
        "name": "Software Engineer",
        "description": "Backend development role"
    })
    print(f"Create role: {response.status_code}")
    if response.ok:
        role_id = response.json()['id']
        print(f"Created role ID: {role_id}")
    
    # List roles
    response = session.get(f"{BASE_URL}/roles/")
    print(f"List roles: {response.status_code}")
    if response.ok:
        print(f"Total roles: {response.json()['count']}")


def test_topics():
    """Test topic endpoints."""
    print("\n=== Testing Topics ===")
    
    # Create topic
    response = session.post(f"{BASE_URL}/topics/", json={
        "name": "Python",
        "description": "Python programming language",
        "difficulty_level": "intermediate"
    })
    print(f"Create topic: {response.status_code}")
    if response.ok:
        topic_id = response.json()['id']
        print(f"Created topic ID: {topic_id}")
    
    # List topics
    response = session.get(f"{BASE_URL}/topics/")
    print(f"List topics: {response.status_code}")
    if response.ok:
        print(f"Total topics: {response.json()['count']}")


def test_questions():
    """Test question endpoints."""
    print("\n=== Testing Questions ===")
    
    # Get first topic
    response = session.get(f"{BASE_URL}/topics/")
    if response.ok and response.json()['count'] > 0:
        topic_id = response.json()['results'][0]['id']
        
        # Create question
        response = session.post(f"{BASE_URL}/questions/", json={
            "topic": topic_id,
            "question_text": "What is a Python decorator?",
            "difficulty": "intermediate",
            "question_type": "technical",
            "expected_answer": "A function that wraps another function"
        })
        print(f"Create question: {response.status_code}")
        if response.ok:
            print(f"Created question ID: {response.json()['id']}")
    
    # List questions
    response = session.get(f"{BASE_URL}/questions/")
    print(f"List questions: {response.status_code}")
    if response.ok:
        print(f"Total questions: {response.json()['count']}")


def test_interview_flow():
    """Test complete interview flow."""
    print("\n=== Testing Interview Flow ===")
    
    # Get role and topic
    role_response = session.get(f"{BASE_URL}/roles/")
    topic_response = session.get(f"{BASE_URL}/topics/")
    
    if role_response.ok and topic_response.ok:
        role_id = role_response.json()['results'][0]['id']
        topic_id = topic_response.json()['results'][0]['id']
        
        # Create interview
        response = session.post(f"{BASE_URL}/interviews/", json={
            "role": role_id,
            "topic": topic_id,
            "difficulty": "intermediate",
            "interview_type": "technical"
        })
        print(f"Create interview: {response.status_code}")
        
        if response.ok:
            interview_id = response.json()['id']
            print(f"Created interview ID: {interview_id}, Status: {response.json()['status']}")
            
            # Start interview
            response = session.post(f"{BASE_URL}/interviews/{interview_id}/start/")
            print(f"Start interview: {response.status_code}")
            if response.ok:
                print(f"Interview status: {response.json()['status']}")
            
            # Add turn
            response = session.post(f"{BASE_URL}/interviews/{interview_id}/turns/", json={
                "question_text": "What is Python?",
                "answer_text": "A high-level programming language"
            })
            print(f"Add turn: {response.status_code}")
            if response.ok:
                print(f"Turn number: {response.json()['turn_number']}")
            
            # Add second turn
            response = session.post(f"{BASE_URL}/interviews/{interview_id}/turns/", json={
                "question_text": "What are Python decorators?",
                "answer_text": "Functions that modify other functions"
            })
            print(f"Add second turn: {response.status_code}")
            if response.ok:
                print(f"Turn number: {response.json()['turn_number']}")
            
            # Pause interview
            response = session.post(f"{BASE_URL}/interviews/{interview_id}/pause/")
            print(f"Pause interview: {response.status_code}")
            if response.ok:
                print(f"Interview status: {response.json()['status']}")
            
            # Resume interview
            response = session.post(f"{BASE_URL}/interviews/{interview_id}/resume/")
            print(f"Resume interview: {response.status_code}")
            if response.ok:
                print(f"Interview status: {response.json()['status']}")
            
            # Finish interview
            response = session.post(f"{BASE_URL}/interviews/{interview_id}/finish/")
            print(f"Finish interview: {response.status_code}")
            if response.ok:
                print(f"Interview status: {response.json()['status']}")
            
            # Get interview details
            response = session.get(f"{BASE_URL}/interviews/{interview_id}/")
            print(f"Get interview: {response.status_code}")
            if response.ok:
                data = response.json()
                print(f"Total turns: {len(data['turns'])}")
                print(f"Interview duration: {data['started_at']} to {data['finished_at']}")


def test_list_interviews():
    """Test listing user's interviews."""
    print("\n=== Testing Interview List ===")
    
    response = session.get(f"{BASE_URL}/interviews/")
    print(f"List interviews: {response.status_code}")
    if response.ok:
        print(f"Total interviews: {response.json()['count']}")


if __name__ == "__main__":
    print("=== Phase 2 API Testing ===\n")
    
    if not login():
        print("Login failed! Make sure you've created a test user.")
        print("Run: python manage.py createsuperuser")
        exit(1)
    
    test_roles()
    test_topics()
    test_questions()
    test_interview_flow()
    test_list_interviews()
    
    print("\n=== Phase 2 Tests Complete ===")
