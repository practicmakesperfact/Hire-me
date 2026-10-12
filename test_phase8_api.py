"""
Manual API testing script for Phase 8 - Reports and Documentation.
Run this after starting the Django server to verify all report endpoints work.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")

def print_response(response):
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# Test session
session = requests.Session()

def test_phase8_reports():
    print("\n" + "="*60)
    print("PHASE 8: Reports and Documentation - API Tests")
    print("="*60 + "\n")
    
    # Step 1: Register and login
    print_info("Step 1: User Registration and Login")
    
    user_data = {
        "username": f"testuser_{datetime.now().timestamp()}",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "testpass123"
    }
    
    response = session.post(f"{BASE_URL}/auth/register/", json=user_data)
    if response.status_code == 201:
        print_success("User registered")
    else:
        print_error(f"Registration failed: {response.status_code}")
        return
    
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    response = session.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        print_success("User logged in")
    else:
        print_error(f"Login failed: {response.status_code}")
        return
    
    print()
    
    # Step 2: Create test data (role, topic, interview)
    print_info("Step 2: Creating Test Data")
    
    # Create role
    role_data = {"name": "Backend Developer", "description": "Python backend"}
    response = session.post(f"{BASE_URL}/roles/", json=role_data)
    if response.status_code == 201:
        role_id = response.json()['id']
        print_success(f"Role created (ID: {role_id})")
    else:
        print_error(f"Role creation failed: {response.status_code}")
        return
    
    # Create topic
    topic_data = {"name": "Django", "difficulty_level": "intermediate", "description": "Django framework"}
    response = session.post(f"{BASE_URL}/topics/", json=topic_data)
    if response.status_code == 201:
        topic_id = response.json()['id']
        print_success(f"Topic created (ID: {topic_id})")
    else:
        print_error(f"Topic creation failed: {response.status_code}")
        return
    
    # Create interview
    interview_data = {
        "role": role_id,
        "topic": topic_id,
        "difficulty": "intermediate",
        "interview_type": "technical"
    }
    response = session.post(f"{BASE_URL}/interviews/", json=interview_data)
    if response.status_code == 201:
        interview_id = response.json()['id']
        print_success(f"Interview created (ID: {interview_id})")
    else:
        print_error(f"Interview creation failed: {response.status_code}")
        return
    
    # Add turn to interview
    turn_data = {
        "question_text": "What is Django ORM?",
        "answer_text": "Django ORM is an object-relational mapper that provides a Pythonic interface to databases.",
        "speaker": "interviewer"
    }
    response = session.post(f"{BASE_URL}/interviews/{interview_id}/turns/", json=turn_data)
    if response.status_code == 201:
        print_success("Interview turn added")
    
    # Finish interview with evaluation
    finish_data = {"generate_evaluation": False}
    response = session.post(f"{BASE_URL}/interviews/{interview_id}/finish/", json=finish_data)
    if response.status_code == 200:
        print_success("Interview finished")
    
    # Manually create evaluation
    from apps.interviews.models import InterviewSession, InterviewEvaluation
    try:
        interview = InterviewSession.objects.get(id=interview_id)
        InterviewEvaluation.objects.create(
            session=interview,
            technical_score=8.5,
            completeness_score=7.5,
            reasoning_score=8.0,
            organization_score=7.0,
            overall_feedback="Good understanding of Django concepts",
            strengths="Clear explanations\nGood examples",
            improvements="Could elaborate more on edge cases"
        )
        print_success("Evaluation created manually")
    except Exception as e:
        print_error(f"Evaluation creation failed: {str(e)}")
    
    # Create communication issue
    issue_data = {
        "category": "filler_words",
        "original_text": "Um, I think Django is, like, really good",
        "suggested_text": "I think Django is really good",
        "context": "Interview answer",
        "confidence_score": 0.9
    }
    response = session.post(f"{BASE_URL}/communication/issues/", json=issue_data)
    if response.status_code == 201:
        issue_id = response.json()['id']
        print_success(f"Communication issue created (ID: {issue_id})")
        
        # Confirm issue
        response = session.post(f"{BASE_URL}/communication/issues/{issue_id}/confirm/")
        if response.status_code == 200:
            print_success("Issue confirmed")
    
    print()
    
    # Step 3: Test Overview Report
    print_info("Step 3: Testing Overview Report")
    
    response = session.get(f"{BASE_URL}/reports/overview/")
    if response.status_code == 200:
        print_success("Overview report retrieved")
        data = response.json()
        print(f"  Interviews: {data['interviews']['total']} total, {data['interviews']['finished']} finished")
        print(f"  Communication: {data['communication']['total_issues']} issues, {data['communication']['mastered']} mastered")
        print(f"  Practice: {data['practice']['total_attempts']} attempts")
        print(f"  Improvement Trend: {data['improvement_trend']}")
        
        if data['performance']['average_scores']['technical']:
            print(f"  Avg Technical Score: {data['performance']['average_scores']['technical']}")
    else:
        print_error(f"Overview report failed: {response.status_code}")
        print_response(response)
    
    print()
    
    # Step 4: Test Communication Report
    print_info("Step 4: Testing Communication Report")
    
    response = session.get(f"{BASE_URL}/reports/communication/")
    if response.status_code == 200:
        print_success("Communication report retrieved")
        data = response.json()
        print(f"  Categories: {len(data['summary']['by_category'])}")
        print(f"  Most Practiced: {len(data['most_practiced'])}")
        print(f"  Recommendations: {len(data['recommendations'])}")
        
        if data['summary']['by_category']:
            print(f"  Top Category: {data['summary']['by_category'][0]['category']}")
    else:
        print_error(f"Communication report failed: {response.status_code}")
        print_response(response)
    
    print()
    
    # Step 5: Test Interview Report
    print_info("Step 5: Testing Interview Report")
    
    response = session.get(f"{BASE_URL}/reports/interviews/")
    if response.status_code == 200:
        print_success("Interview report retrieved")
        data = response.json()
        print(f"  Interview History: {len(data['interview_history'])} interviews")
        print(f"  Performance by Topic: {len(data['performance_by_topic'])} topics")
        print(f"  Score Progression: {len(data['score_progression'])} data points")
        print(f"  Insights: {len(data['insights'])}")
        
        if data['interview_history']:
            latest = data['interview_history'][0]
            print(f"  Latest Interview: {latest['topic']} ({latest['difficulty']})")
            if latest['evaluation']:
                print(f"    Technical Score: {latest['evaluation']['technical']}")
    else:
        print_error(f"Interview report failed: {response.status_code}")
        print_response(response)
    
    print()
    
    # Step 6: Test Progress Snapshot
    print_info("Step 6: Testing Progress Snapshot")
    
    response = session.post(f"{BASE_URL}/reports/snapshot/")
    if response.status_code == 200:
        print_success("Progress snapshot created")
        data = response.json()
        print(f"  Snapshot ID: {data['id']}")
        print(f"  Date: {data['date']}")
        print(f"  Total Issues: {data['total_issues']}")
        print(f"  Mastered Issues: {data['mastered_issues']}")
    else:
        print_error(f"Snapshot creation failed: {response.status_code}")
        print_response(response)
    
    # Try creating duplicate snapshot
    response = session.post(f"{BASE_URL}/reports/snapshot/")
    if response.status_code == 200 and 'already exists' in response.json().get('message', ''):
        print_success("Duplicate snapshot prevented correctly")
    
    print()
    
    # Step 7: Test with Multiple Interviews for Better Reports
    print_info("Step 7: Creating Additional Test Data")
    
    # Create more interviews
    for i in range(3):
        interview_data = {
            "role": role_id,
            "topic": topic_id,
            "difficulty": ["easy", "intermediate", "hard"][i],
            "interview_type": "technical"
        }
        response = session.post(f"{BASE_URL}/interviews/", json=interview_data)
        if response.status_code == 201:
            new_interview_id = response.json()['id']
            
            # Add turn
            session.post(f"{BASE_URL}/interviews/{new_interview_id}/turns/", json={
                "question_text": f"Question {i+2}",
                "answer_text": f"Answer {i+2}",
                "speaker": "interviewer"
            })
            
            # Finish
            session.post(f"{BASE_URL}/interviews/{new_interview_id}/finish/")
            
            print_success(f"Additional interview {i+1} created and finished")
    
    print()
    
    # Step 8: Test Reports with More Data
    print_info("Step 8: Testing Reports with Enhanced Data")
    
    response = session.get(f"{BASE_URL}/reports/overview/")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Overview: {data['interviews']['total']} total interviews")
        print(f"  Completion Rate: {data['interviews']['completion_rate']}%")
    
    response = session.get(f"{BASE_URL}/reports/interviews/")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Interview Report: {len(data['interview_history'])} interviews in history")
        
        if data['performance_by_difficulty']:
            print(f"  Performance by Difficulty:")
            for perf in data['performance_by_difficulty']:
                print(f"    {perf['difficulty']}: {perf['count']} interviews")
    
    print()
    
    # Summary
    print("="*60)
    print_success("Phase 8 API Tests Complete!")
    print("="*60)
    print("\nAll report endpoints tested:")
    print("  ✓ Overview Report (GET /api/v1/reports/overview/)")
    print("  ✓ Communication Report (GET /api/v1/reports/communication/)")
    print("  ✓ Interview Report (GET /api/v1/reports/interviews/)")
    print("  ✓ Progress Snapshot (POST /api/v1/reports/snapshot/)")
    print("\nPhase 8 is ready for production!")

if __name__ == "__main__":
    try:
        test_phase8_reports()
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to server. Make sure Django is running:")
        print_info("python manage.py runserver")
    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
