"""
Test suite for Resilience Coach Agent API
Tests input validation, error handling, and API responses
"""
import requests
import json
import time

# Configuration
API_URL = "http://localhost:5000"
RESILIENCE_ENDPOINT = f"{API_URL}/resilience"
HEALTH_ENDPOINT = f"{API_URL}/health"


def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"   {details}")
    print()


def test_health_check():
    """Test health check endpoint"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(HEALTH_ENDPOINT)
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get('status') == 'ok' and
            data.get('agent') == 'resilience_coach'
        )
        
        print_test("Health Check", passed, f"Response: {data}")
        return passed
    except Exception as e:
        print_test("Health Check", False, f"Error: {e}")
        return False


def test_valid_request():
    """Test valid request"""
    print("=" * 60)
    print("TEST 2: Valid Request")
    print("=" * 60)
    
    payload = {
        "agent": "resilience_coach",
        "input_text": "I'm feeling really stressed and anxious about my exams",
        "metadata": {
            "user_id": "test_user_1",
            "language": "en"
        }
    }
    
    try:
        response = requests.post(RESILIENCE_ENDPOINT, json=payload)
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get('status') == 'success' and
            'analysis' in data and
            'recommendation' in data and
            'message' in data
        )
        
        if passed:
            print(f"Sentiment: {data['analysis']['sentiment']}")
            print(f"Stress Level: {data['analysis']['stress_level']}")
            print(f"Emotions: {data['analysis']['emotions']}")
            print(f"Recommendation: {data['recommendation']['type']}")
            print(f"Message: {data['message'][:100]}...")
        
        print_test("Valid Request", passed)
        return passed
    except Exception as e:
        print_test("Valid Request", False, f"Error: {e}")
        return False


def test_empty_input():
    """Test empty input validation"""
    print("=" * 60)
    print("TEST 3: Empty Input Validation")
    print("=" * 60)
    
    payload = {
        "agent": "resilience_coach",
        "input_text": "",
        "metadata": {}
    }
    
    try:
        response = requests.post(RESILIENCE_ENDPOINT, json=payload)
        data = response.json()
        
        passed = (
            response.status_code == 400 and
            data.get('status') == 'error'
        )
        
        print_test("Empty Input Rejection", passed, f"Message: {data.get('message')}")
        return passed
    except Exception as e:
        print_test("Empty Input Rejection", False, f"Error: {e}")
        return False


def test_very_short_input():
    """Test very short input"""
    print("=" * 60)
    print("TEST 4: Very Short Input")
    print("=" * 60)
    
    payload = {
        "agent": "resilience_coach",
        "input_text": "ok",
        "metadata": {}
    }
    
    try:
        response = requests.post(RESILIENCE_ENDPOINT, json=payload)
        data = response.json()
        
        passed = (
            response.status_code == 400 and
            data.get('status') == 'error'
        )
        
        print_test("Short Input Rejection", passed, f"Message: {data.get('message')}")
        return passed
    except Exception as e:
        print_test("Short Input Rejection", False, f"Error: {e}")
        return False


def test_too_long_input():
    """Test input that's too long"""
    print("=" * 60)
    print("TEST 5: Too Long Input")
    print("=" * 60)
    
    payload = {
        "agent": "resilience_coach",
        "input_text": "a" * 3000,  # Exceeds max length
        "metadata": {}
    }
    
    try:
        response = requests.post(RESILIENCE_ENDPOINT, json=payload)
        data = response.json()
        
        passed = (
            response.status_code == 400 and
            data.get('status') == 'error'
        )
        
        print_test("Long Input Rejection", passed, f"Message: {data.get('message')}")
        return passed
    except Exception as e:
        print_test("Long Input Rejection", False, f"Error: {e}")
        return False


def test_spam_input():
    """Test spam/gibberish detection"""
    print("=" * 60)
    print("TEST 6: Spam Detection")
    print("=" * 60)
    
    payload = {
        "agent": "resilience_coach",
        "input_text": "aaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "metadata": {}
    }
    
    try:
        response = requests.post(RESILIENCE_ENDPOINT, json=payload)
        data = response.json()
        
        passed = (
            response.status_code == 400 and
            data.get('status') == 'error'
        )
        
        print_test("Spam Detection", passed, f"Message: {data.get('message')}")
        return passed
    except Exception as e:
        print_test("Spam Detection", False, f"Error: {e}")
        return False


def test_missing_agent_field():
    """Test missing agent field"""
    print("=" * 60)
    print("TEST 7: Missing Agent Field")
    print("=" * 60)
    
    payload = {
        "input_text": "I feel sad",
        "metadata": {}
    }
    
    try:
        response = requests.post(RESILIENCE_ENDPOINT, json=payload)
        data = response.json()
        
        passed = (
            response.status_code == 400 and
            data.get('status') == 'error'
        )
        
        print_test("Missing Agent Field", passed, f"Message: {data.get('message')}")
        return passed
    except Exception as e:
        print_test("Missing Agent Field", False, f"Error: {e}")
        return False


def test_wrong_agent_name():
    """Test wrong agent name"""
    print("=" * 60)
    print("TEST 8: Wrong Agent Name")
    print("=" * 60)
    
    payload = {
        "agent": "wrong_agent",
        "input_text": "I feel sad",
        "metadata": {}
    }
    
    try:
        response = requests.post(RESILIENCE_ENDPOINT, json=payload)
        data = response.json()
        
        passed = (
            response.status_code == 400 and
            data.get('status') == 'error'
        )
        
        print_test("Wrong Agent Name", passed, f"Message: {data.get('message')}")
        return passed
    except Exception as e:
        print_test("Wrong Agent Name", False, f"Error: {e}")
        return False


def test_xss_attempt():
    """Test XSS injection prevention"""
    print("=" * 60)
    print("TEST 9: XSS Prevention")
    print("=" * 60)
    
    payload = {
        "agent": "resilience_coach",
        "input_text": "<script>alert('xss')</script>",
        "metadata": {}
    }
    
    try:
        response = requests.post(RESILIENCE_ENDPOINT, json=payload)
        data = response.json()
        
        passed = (
            response.status_code == 400 and
            data.get('status') == 'error'
        )
        
        print_test("XSS Prevention", passed, f"Message: {data.get('message')}")
        return passed
    except Exception as e:
        print_test("XSS Prevention", False, f"Error: {e}")
        return False


def test_multiple_emotions():
    """Test handling different emotional states"""
    print("=" * 60)
    print("TEST 10: Multiple Emotional States")
    print("=" * 60)
    
    test_cases = [
        "I'm feeling overwhelmed with work and can't sleep",
        "I feel sad and lonely today",
        "I'm angry and frustrated with everything",
        "I'm happy but a bit nervous about tomorrow"
    ]
    
    all_passed = True
    for i, test_input in enumerate(test_cases, 1):
        payload = {
            "agent": "resilience_coach",
            "input_text": test_input,
            "metadata": {"user_id": f"test_{i}"}
        }
        
        try:
            response = requests.post(RESILIENCE_ENDPOINT, json=payload)
            data = response.json()
            
            passed = (
                response.status_code == 200 and
                data.get('status') == 'success'
            )
            
            if passed:
                print(f"  {i}. Input: {test_input[:50]}...")
                print(f"     Emotions: {data['analysis']['emotions']}")
                print(f"     Recommendation: {data['recommendation']['type']}")
            
            all_passed = all_passed and passed
            
        except Exception as e:
            print(f"  {i}. FAILED: {e}")
            all_passed = False
    
    print_test("Multiple Emotional States", all_passed)
    return all_passed


def test_invalid_content_type():
    """Test non-JSON content type"""
    print("=" * 60)
    print("TEST 11: Invalid Content Type")
    print("=" * 60)
    
    try:
        response = requests.post(
            RESILIENCE_ENDPOINT,
            data="not json",
            headers={'Content-Type': 'text/plain'}
        )
        data = response.json()
        
        passed = (
            response.status_code == 400 and
            data.get('status') == 'error'
        )
        
        print_test("Invalid Content Type", passed, f"Message: {data.get('message')}")
        return passed
    except Exception as e:
        print_test("Invalid Content Type", False, f"Error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RESILIENCE COACH AGENT - API TEST SUITE")
    print("=" * 60 + "\n")
    
    # Check if server is running
    try:
        requests.get(HEALTH_ENDPOINT, timeout=2)
    except:
        print("❌ ERROR: Server is not running!")
        print("Please start the server with: python -m backend.app")
        return
    
    results = []
    
    # Run tests
    results.append(test_health_check())
    results.append(test_valid_request())
    results.append(test_empty_input())
    results.append(test_very_short_input())
    results.append(test_too_long_input())
    results.append(test_spam_input())
    results.append(test_missing_agent_field())
    results.append(test_wrong_agent_name())
    results.append(test_xss_attempt())
    results.append(test_multiple_emotions())
    results.append(test_invalid_content_type())
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
