"""
Phase 6 API test script - English Improvement Lab
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


def setup_practice_data():
    """Create interview with issues for practice."""
    print("\n=== Setting Up Practice Data ===")
    
    # Get roles and topics
    roles = session.get(f"{BASE_URL}/roles/").json()
    topics = session.get(f"{BASE_URL}/topics/").json()
    
    if roles['count'] == 0 or topics['count'] == 0:
        print("Run: python manage.py seed_data")
        return None
    
    # Create interview
    interview = session.post(f"{BASE_URL}/interviews/", json={
        "role": roles['results'][0]['id'],
        "topic": topics['results'][0]['id'],
        "difficulty": "intermediate",
        "interview_type": "technical"
    }).json()
    
    interview_id = interview['id']
    
    # Start and add answers with issues
    session.post(f"{BASE_URL}/interviews/{interview_id}/start/")
    
    session.post(f"{BASE_URL}/interviews/{interview_id}/answer_and_continue/", json={
        "question_text": "What is Python?",
        "answer_text": "Um, well, Python is is a programming language. Like, it's really really popular."
    })
    
    # Finish and analyze
    session.post(f"{BASE_URL}/interviews/{interview_id}/finish/", json={"generate_evaluation": False})
    session.post(f"{BASE_URL}/communication/analyze/{interview_id}/")
    
    print(f"Created interview {interview_id} with communication issues")
    
    # Confirm first issue for practice
    issues = session.get(f"{BASE_URL}/communication/issues/?status=needs_review").json()
    if issues['count'] > 0:
        issue_id = issues['results'][0]['id']
        session.post(f"{BASE_URL}/communication/issues/{issue_id}/confirm/")
        print(f"Confirmed issue {issue_id} for practice")
        return issue_id
    
    return None


def test_practice_queue():
    """Test getting practice queue."""
    print("\n=== Testing Practice Queue ===")
    
    response = session.get(f"{BASE_URL}/practice/queue/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Practice queue count: {data['count']}")
        
        for item in data['items'][:3]:
            print(f"\n  Issue #{item['id']}")
            print(f"  Category: {item['category_display']}")
            print(f"  Original: {item['original_text'][:50]}...")
            if item['proposed_correction']:
                print(f"  Target: {item['proposed_correction'][:50]}...")
            print(f"  Practice count: {item['practice_count']}")


def test_practice_queue_filtering():
    """Test filtering practice queue by category."""
    print("\n=== Testing Queue Filtering ===")
    
    categories = ['grammar', 'filler_words', 'repeated_words']
    
    for category in categories:
        response = session.get(f"{BASE_URL}/practice/queue/?category={category}")
        if response.ok:
            count = response.json()['count']
            print(f"  {category}: {count} items")


def test_generate_reference_audio(issue_id):
    """Test generating reference audio."""
    print("\n=== Testing Reference Audio Generation ===")
    
    response = session.post(f"{BASE_URL}/practice/issues/{issue_id}/reference-audio/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Audio URL: {data['audio_url']}")
        print(f"Text: {data['text']}")
    else:
        print(f"Error: {response.text}")
        print("Note: Requires Piper TTS installed")


def test_submit_practice():
    """Test submitting practice attempt."""
    print("\n=== Testing Practice Submission ===")
    
    # Get first issue from queue
    queue = session.get(f"{BASE_URL}/practice/queue/").json()
    
    if queue['count'] == 0:
        print("No issues in practice queue")
        return
    
    issue = queue['items'][0]
    target_text = issue['proposed_correction'] or issue['original_text']
    
    # Submit perfect attempt
    response = session.post(f"{BASE_URL}/practice/submit/", json={
        "issue_id": issue['id'],
        "attempt_text": target_text
    })
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Score: {data['score']}/10")
        print(f"Feedback: {data['feedback']}")
        print(f"Attempt ID: {data['id']}")
    
    # Submit imperfect attempt
    response = session.post(f"{BASE_URL}/practice/submit/", json={
        "issue_id": issue['id'],
        "attempt_text": "This is different text"
    })
    
    if response.ok:
        data = response.json()
        print(f"\nImperfect attempt score: {data['score']}/10")
        print(f"Feedback: {data['feedback']}")


def test_practice_history():
    """Test getting practice history."""
    print("\n=== Testing Practice History ===")
    
    response = session.get(f"{BASE_URL}/practice/history/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        attempts = response.json()
        print(f"Total attempts: {len(attempts)}")
        
        for attempt in attempts[:3]:
            print(f"\n  Attempt #{attempt['id']}")
            print(f"  Category: {attempt['issue_category']}")
            print(f"  Score: {attempt['score']}")
            print(f"  Feedback: {attempt['feedback']}")


def test_progress():
    """Test getting progress overview."""
    print("\n=== Testing Progress Overview ===")
    
    response = session.get(f"{BASE_URL}/practice/progress/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        
        print("\nIssue Status:")
        issues = data['issues']
        print(f"  Total: {issues['total']}")
        print(f"  Needs Review: {issues['needs_review']}")
        print(f"  Confirmed: {issues['confirmed']}")
        print(f"  Practicing: {issues['practicing']}")
        print(f"  Mastered: {issues['mastered']}")
        
        print("\nPractice Stats:")
        practice = data['practice']
        print(f"  Total attempts: {practice['total_attempts']}")
        print(f"  Recent (7 days): {practice['recent_attempts_7d']}")
        if practice['average_score']:
            print(f"  Average score: {practice['average_score']}/10")
        
        print(f"\nCompletion rate: {data['completion_rate']}%")


def test_mark_mastered():
    """Test manually marking issue as mastered."""
    print("\n=== Testing Mark as Mastered ===")
    
    # Get a practicing issue
    issues = session.get(f"{BASE_URL}/communication/issues/?status=practicing").json()
    
    if issues['count'] == 0:
        print("No practicing issues found")
        return
    
    issue_id = issues['results'][0]['id']
    
    response = session.post(f"{BASE_URL}/practice/issues/{issue_id}/master/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        print(f"Issue #{issue_id} marked as mastered")
        print(f"New status: {response.json()['status']}")


if __name__ == "__main__":
    print("=== Phase 6 English Improvement Lab Testing ===")
    print("\nThis phase provides practice interface for communication issues.\n")
    
    if not login():
        print("\nLogin failed! Create test user first.")
        exit(1)
    
    # Setup test data
    issue_id = setup_practice_data()
    
    # Test practice features
    test_practice_queue()
    test_practice_queue_filtering()
    
    if issue_id:
        test_generate_reference_audio(issue_id)
    
    test_submit_practice()
    test_practice_history()
    test_progress()
    test_mark_mastered()
    
    print("\n=== Phase 6 Tests Complete ===")
    print("\nKey Features:")
    print("  - Practice queue with confirmed issues")
    print("  - Reference audio generation for target pronunciation")
    print("  - Practice attempt submission and scoring")
    print("  - Automatic mastery after 3 good attempts")
    print("  - Progress tracking and statistics")
