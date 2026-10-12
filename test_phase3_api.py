"""
Phase 3 API test script - LLM Integration
Run after: python manage.py runserver
Requires: Ollama running with a model pulled
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


def create_interview():
    """Create and start an interview."""
    print("\n=== Creating Interview ===")
    
    # Get role and topic
    roles = session.get(f"{BASE_URL}/roles/").json()
    topics = session.get(f"{BASE_URL}/topics/").json()
    
    if roles['count'] == 0 or topics['count'] == 0:
        print("No roles or topics found. Run: python manage.py seed_data")
        return None
    
    role_id = roles['results'][0]['id']
    topic_id = topics['results'][0]['id']
    
    response = session.post(f"{BASE_URL}/interviews/", json={
        "role": role_id,
        "topic": topic_id,
        "difficulty": "intermediate",
        "interview_type": "technical"
    })
    
    if response.ok:
        interview_id = response.json()['id']
        print(f"Created interview ID: {interview_id}")
        
        # Start interview
        session.post(f"{BASE_URL}/interviews/{interview_id}/start/")
        print(f"Started interview")
        
        return interview_id
    
    return None


def test_llm_question_generation(interview_id):
    """Test LLM-based question generation."""
    print("\n=== Testing LLM Question Generation ===")
    
    response = session.post(
        f"{BASE_URL}/interviews/{interview_id}/next_question/",
        json={"use_llm": True}
    )
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Generated Question: {data['question']}")
        print(f"Turn Number: {data['turn_number']}")
        return data['question']
    else:
        print(f"Error: {response.text}")
        print("\nNote: Make sure Ollama is running:")
        print("  1. ollama serve")
        print("  2. ollama pull llama3.2:3b")
        return None


def test_fallback_question_generation(interview_id):
    """Test fallback to question bank."""
    print("\n=== Testing Fallback Question (No LLM) ===")
    
    response = session.post(
        f"{BASE_URL}/interviews/{interview_id}/next_question/",
        json={"use_llm": False}
    )
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Question from Bank: {data['question']}")
        return data['question']
    else:
        print(f"Error: {response.text}")
        return None


def test_answer_and_continue(interview_id, question):
    """Test answering and getting next question."""
    print("\n=== Testing Answer & Continue ===")
    
    response = session.post(
        f"{BASE_URL}/interviews/{interview_id}/answer_and_continue/",
        json={
            "question_text": question,
            "answer_text": "Python is a high-level, interpreted programming language known for its simplicity and readability."
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Turn saved: {data['turn_number']}")
        print(f"Next question: {data.get('next_question', 'None')}")
        return True
    else:
        print(f"Error: {response.text}")
        return False


def test_finish_with_evaluation(interview_id):
    """Test finishing interview with LLM evaluation."""
    print("\n=== Testing Finish with Evaluation ===")
    
    response = session.post(
        f"{BASE_URL}/interviews/{interview_id}/finish/",
        json={"generate_evaluation": True}
    )
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Interview Status: {data['status']}")
        
        if 'evaluation' in data and data['evaluation']:
            eval_data = data['evaluation']
            print("\nEvaluation Scores:")
            print(f"  Technical: {eval_data.get('technical_score', 'N/A')}")
            print(f"  Completeness: {eval_data.get('completeness_score', 'N/A')}")
            print(f"  Reasoning: {eval_data.get('reasoning_score', 'N/A')}")
            print(f"  Organization: {eval_data.get('organization_score', 'N/A')}")
            print(f"\nFeedback: {eval_data.get('overall_feedback', 'N/A')}")
        else:
            print("\nNo evaluation generated (Ollama may not be available)")
    else:
        print(f"Error: {response.text}")


def test_get_report(interview_id):
    """Test getting interview report."""
    print("\n=== Testing Get Report ===")
    
    response = session.get(f"{BASE_URL}/interviews/{interview_id}/report/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print("\nReport:")
        print(f"  Technical Score: {data.get('technical_score', 'N/A')}")
        print(f"  Overall Feedback: {data.get('overall_feedback', 'N/A')[:100]}...")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("=== Phase 3 LLM Integration Testing ===")
    print("\nPrerequisites:")
    print("  - Ollama running: ollama serve")
    print("  - Model pulled: ollama pull llama3.2:3b")
    print("  - Seed data: python manage.py seed_data")
    print()
    
    if not login():
        print("\nLogin failed! Create test user first.")
        exit(1)
    
    # Create interview
    interview_id = create_interview()
    if not interview_id:
        print("Failed to create interview")
        exit(1)
    
    # Test LLM question generation
    llm_question = test_llm_question_generation(interview_id)
    
    # Test fallback if LLM not available
    if not llm_question:
        fallback_question = test_fallback_question_generation(interview_id)
        llm_question = fallback_question
    
    if llm_question:
        # Test answer and continue
        test_answer_and_continue(interview_id, llm_question)
        
        # Add another turn
        next_q = test_fallback_question_generation(interview_id)
        if next_q:
            test_answer_and_continue(interview_id, next_q)
    
    # Test finish with evaluation
    test_finish_with_evaluation(interview_id)
    
    # Test get report
    test_get_report(interview_id)
    
    print("\n=== Phase 3 Tests Complete ===")
