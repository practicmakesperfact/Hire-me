"""
Phase 5 API test script - Communication Issue Logging
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


def create_interview_with_issues():
    """Create an interview and answer with communication issues."""
    print("\n=== Creating Interview with Communication Issues ===")
    
    # Get role and topic
    roles = session.get(f"{BASE_URL}/roles/").json()
    topics = session.get(f"{BASE_URL}/topics/").json()
    
    if roles['count'] == 0 or topics['count'] == 0:
        print("No roles or topics. Run: python manage.py seed_data")
        return None
    
    # Create and start interview
    response = session.post(f"{BASE_URL}/interviews/", json={
        "role": roles['results'][0]['id'],
        "topic": topics['results'][0]['id'],
        "difficulty": "intermediate",
        "interview_type": "technical"
    })
    
    if not response.ok:
        print(f"Failed to create interview: {response.text}")
        return None
    
    interview_id = response.json()['id']
    session.post(f"{BASE_URL}/interviews/{interview_id}/start/")
    print(f"Created interview ID: {interview_id}")
    
    # Answer with communication issues
    answer_with_issues = """
    Um, well, like, Python is, uh, Python is a programming language.
    I think Python Python is really really good. You know, it's, like,
    really popular and, uh, basically Python is is used everywhere.
    """
    
    response = session.post(
        f"{BASE_URL}/interviews/{interview_id}/answer_and_continue/",
        json={
            "question_text": "What is Python?",
            "answer_text": answer_with_issues
        }
    )
    
    if response.ok:
        print("Added answer with issues")
        print(f"Issues detected: {response.json().get('issues_detected', 'N/A')}")
    
    return interview_id


def test_analyze_session(interview_id):
    """Test analyzing entire session."""
    print("\n=== Analyzing Interview Session ===")
    
    response = session.post(f"{BASE_URL}/communication/analyze/{interview_id}/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Message: {data['message']}")
        print(f"Stats: {data['stats']}")
    else:
        print(f"Error: {response.text}")


def test_list_issues():
    """Test listing communication issues."""
    print("\n=== Listing Communication Issues ===")
    
    response = session.get(f"{BASE_URL}/communication/issues/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Total issues: {data['count']}")
        
        for issue in data['results'][:3]:  # Show first 3
            print(f"\n  Issue #{issue['id']}")
            print(f"  Category: {issue['category_display']}")
            print(f"  Status: {issue['status_display']}")
            print(f"  Original: {issue['original_text'][:50]}...")
            if issue['proposed_correction']:
                print(f"  Correction: {issue['proposed_correction'][:50]}...")


def test_filter_by_category():
    """Test filtering issues by category."""
    print("\n=== Filtering by Category ===")
    
    categories = ['filler_words', 'repeated_words', 'grammar']
    
    for category in categories:
        response = session.get(f"{BASE_URL}/communication/issues/?category={category}")
        if response.ok:
            count = response.json()['count']
            print(f"  {category}: {count} issues")


def test_confirm_issue():
    """Test confirming an issue."""
    print("\n=== Confirming Issue ===")
    
    # Get first issue
    response = session.get(f"{BASE_URL}/communication/issues/?status=needs_review")
    if response.ok and response.json()['count'] > 0:
        issue_id = response.json()['results'][0]['id']
        
        # Confirm it
        response = session.post(f"{BASE_URL}/communication/issues/{issue_id}/confirm/")
        print(f"Confirm status: {response.status_code}")
        if response.ok:
            print(f"Issue confirmed: {response.json()['status']}")


def test_dismiss_issue():
    """Test dismissing an issue."""
    print("\n=== Dismissing Issue ===")
    
    # Get second issue
    response = session.get(f"{BASE_URL}/communication/issues/?status=needs_review")
    if response.ok and response.json()['count'] > 1:
        issue_id = response.json()['results'][1]['id']
        
        # Dismiss it
        response = session.post(f"{BASE_URL}/communication/issues/{issue_id}/dismiss/")
        print(f"Dismiss status: {response.status_code}")
        if response.ok:
            print(f"Issue dismissed: {response.json()['status']}")


def test_issue_summary():
    """Test getting issue summary."""
    print("\n=== Issue Summary ===")
    
    response = session.get(f"{BASE_URL}/communication/summary/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"\nTotal issues: {data['total_issues']}")
        print(f"Needs review: {data['needs_review']}")
        print(f"Practicing: {data['practicing']}")
        print(f"Mastered: {data['mastered']}")
        
        print("\nBy category:")
        for cat, count in data.get('by_category', {}).items():
            print(f"  {cat}: {count}")


if __name__ == "__main__":
    print("=== Phase 5 Communication Issue Logging Testing ===")
    print("\nThis phase tests SILENT issue detection during interviews.")
    print("Issues are logged but NOT shown to user during interview.\n")
    
    if not login():
        print("\nLogin failed! Create test user first.")
        exit(1)
    
    # Create interview with communication issues
    interview_id = create_interview_with_issues()
    
    if interview_id:
        # Analyze the session
        test_analyze_session(interview_id)
        
        # Test issue management
        test_list_issues()
        test_filter_by_category()
        test_confirm_issue()
        test_dismiss_issue()
        test_issue_summary()
    
    print("\n=== Phase 5 Tests Complete ===")
    print("\nKey Points:")
    print("  - Issues detected silently during interview")
    print("  - User can review issues AFTER interview")
    print("  - User can confirm or dismiss false positives")
    print("  - Issues tracked for practice in Phase 6")
