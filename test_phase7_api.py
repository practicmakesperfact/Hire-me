"""
Phase 7 API test script - RAG Knowledge Base
Run after: python manage.py runserver
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
session = requests.Session()


def login():
    """Login with admin user (required for imports)."""
    response = session.post(f"{BASE_URL}/auth/login/", json={
        "username": "admin",
        "password": "admin"
    })
    print(f"Login: {response.status_code}")
    if not response.ok:
        print("Note: Create admin user with: python manage.py createsuperuser")
    return response.ok


def test_import_document():
    """Test importing a document."""
    print("\n=== Testing Document Import ===")
    
    # Sample Python documentation snippet
    content = """
    Python is a high-level, interpreted programming language. 
    It emphasizes code readability with significant whitespace.
    
    Python supports multiple programming paradigms including:
    - Object-oriented programming
    - Procedural programming
    - Functional programming
    
    Key features:
    - Dynamic typing
    - Automatic memory management
    - Large standard library
    - Third-party package ecosystem (PyPI)
    
    Python decorators are functions that modify other functions.
    They are defined using the @ syntax.
    
    List comprehensions provide a concise way to create lists.
    Syntax: [expression for item in iterable if condition]
    """
    
    response = session.post(f"{BASE_URL}/knowledge/import/", json={
        "title": "Python Basics",
        "content": content,
        "source_url": "https://docs.python.org",
        "license_info": "PSF License",
        "version": "3.11"
    })
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Imported: {data['title']}")
        print(f"Source ID: {data['id']}")
        print(f"Chunks: {data['chunk_count']}")
        return data['id']
    else:
        print(f"Error: {response.text}")
        return None


def test_list_sources():
    """Test listing knowledge sources."""
    print("\n=== Testing Source List ===")
    
    response = session.get(f"{BASE_URL}/knowledge/list/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Total sources: {data['count']}")
        
        for source in data['sources']:
            print(f"\n  Source: {source['title']}")
            print(f"  URL: {source['url']}")
            print(f"  Chunks: {source['chunk_count']}")
            print(f"  License: {source['license']}")


def test_search_knowledge():
    """Test searching knowledge base."""
    print("\n=== Testing Knowledge Search ===")
    
    queries = [
        'Python programming',
        'decorator',
        'list comprehension'
    ]
    
    for query in queries:
        response = session.post(f"{BASE_URL}/knowledge/search/", json={
            "query": query,
            "limit": 3
        })
        
        if response.ok:
            data = response.json()
            print(f"\nQuery: '{query}'")
            print(f"Results: {data['results_count']}")
            
            for result in data['results'][:2]:
                print(f"  Source: {result['source_title']}")
                print(f"  Content: {result['content'][:100]}...")
                print(f"  Relevance: {result['relevance_score']:.2f}")


def test_verify_answer():
    """Test answer verification."""
    print("\n=== Testing Answer Verification ===")
    
    test_cases = [
        {
            "question": "What is Python?",
            "answer": "Python is a high-level interpreted programming language",
            "topic": "Python"
        },
        {
            "question": "What are decorators?",
            "answer": "Decorators are functions that modify other functions",
            "topic": "Python"
        },
        {
            "question": "What is Java?",
            "answer": "Java is a compiled language",
            "topic": "Java"
        }
    ]
    
    for case in test_cases:
        response = session.post(f"{BASE_URL}/knowledge/verify/", json=case)
        
        if response.ok:
            data = response.json()
            print(f"\nQ: {case['question']}")
            print(f"A: {case['answer'][:50]}...")
            print(f"Verified: {data['verified']}")
            print(f"Confidence: {data['confidence']:.2f}")
            print(f"Message: {data['message']}")
            
            if data['sources']:
                print(f"Supporting sources: {len(data['sources'])}")


def test_source_stats(source_id):
    """Test getting source statistics."""
    print("\n=== Testing Source Stats ===")
    
    response = session.get(f"{BASE_URL}/knowledge/sources/{source_id}/stats/")
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Source: {data['title']}")
        print(f"Chunks: {data['chunk_count']}")
        print(f"Total words: {data['total_words']}")
        print(f"Avg chunk size: {data['avg_chunk_size']} words")


def test_interview_with_rag():
    """Test that interviews use RAG for questions."""
    print("\n=== Testing Interview with RAG ===")
    
    # Get roles and topics
    roles = session.get(f"{BASE_URL}/roles/").json()
    topics = session.get(f"{BASE_URL}/topics/").json()
    
    if roles['count'] == 0 or topics['count'] == 0:
        print("Run: python manage.py seed_data")
        return
    
    # Create interview
    interview = session.post(f"{BASE_URL}/interviews/", json={
        "role": roles['results'][0]['id'],
        "topic": topics['results'][0]['id'],
        "difficulty": "intermediate",
        "interview_type": "technical"
    }).json()
    
    interview_id = interview['id']
    
    # Start
    session.post(f"{BASE_URL}/interviews/{interview_id}/start/")
    
    # Generate question (should use RAG context)
    response = session.post(f"{BASE_URL}/interviews/{interview_id}/next_question/", json={
        "use_llm": True
    })
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Generated question (with RAG context):")
        print(f"  {data['question']}")
    else:
        print("Note: Requires Ollama running")


if __name__ == "__main__":
    print("=== Phase 7 RAG Knowledge Base Testing ===")
    print("\nThis phase adds document import and retrieval for grounded questions.\n")
    
    if not login():
        print("\nLogin failed! Create admin user for document import.")
        print("Run: python manage.py createsuperuser")
        exit(1)
    
    # Test document import
    source_id = test_import_document()
    
    # Test knowledge features
    test_list_sources()
    test_search_knowledge()
    test_verify_answer()
    
    if source_id:
        test_source_stats(source_id)
    
    # Test integration with interviews
    test_interview_with_rag()
    
    print("\n=== Phase 7 Tests Complete ===")
    print("\nKey Features:")
    print("  - Import documentation as knowledge sources")
    print("  - Search knowledge base with keyword matching")
    print("  - Verify answers against documentation")
    print("  - Interviews use RAG context for question generation")
    print("  - Source attribution and licensing")
