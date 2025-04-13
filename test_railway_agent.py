import pytest
import json
import asyncio
from typing import Dict, Any


from railway_agent_openai import railway_agent

try:
    from railway_agent_openai import railway_agent  # Default to OpenAI implementation
except ImportError:
    # This is just a placeholder that will fail tests if no implementation is found
    async def railway_agent(query: str) -> Dict[str, Any]:
        return {}
# Helper function to run async tests
async def _test_railway_agent(query: str) -> Dict[str, Any]:
    return await railway_agent(query)
def run_async_test(query: str) -> Dict[str, Any]:
    """Run the railway agent in an asyncio loop"""
    return asyncio.run(_test_railway_agent(query))
# Tests for basic functionality
def test_basic_query_structure():
    """Test that a basic query returns the correct structure"""
    response = run_async_test("Find trains from Delhi to Mumbai")
    
    # Check response type
    assert isinstance(response, dict), "Response should be a dictionary"
    
    # Check for required keys
    required_keys = ["source", "destination", "date", "class", "trains"]
    for key in required_keys:
        assert key in response, f"Response missing required key: {key}"
    
    # Check source and destination
    assert response["source"] == "Delhi", f"Source should be Delhi, got {response['source']}"
    assert response["destination"] == "Mumbai", f"Destination should be Mumbai, got {response['destination']}"
    
    # Check trains array
    assert isinstance(response["trains"], list), "Trains should be an array"
def test_class_extraction():
    """Test that the agent correctly extracts class information"""
    response = run_async_test("Show trains from Chennai to Bangalore in sleeper class")
    
    # Check class extraction
    assert response["class"] == "SL", f"Class should be SL for sleeper, got {response['class']}"
    
    # Check source and destination
    assert response["source"] == "Chennai", f"Source should be Chennai, got {response['source']}"
    assert response["destination"] == "Bangalore", f"Destination should be Bangalore, got {response['destination']}"
def test_no_trains_route():
    """Test that the agent handles routes with no trains correctly"""
    response = run_async_test("Any trains between Delhi and Leh?")
    
    # Check source and destination
    assert response["source"] == "Delhi", f"Source should be Delhi, got {response['source']}"
    assert response["destination"] == "Leh", f"Destination should be Leh, got {response['destination']}"
    
    # Check that trains array is empty
    assert isinstance(response["trains"], list), "Trains should be an array"
    assert len(response["trains"]) == 0, f"Trains array should be empty for a route with no trains, got {len(response['trains'])} trains"
def test_date_extraction():
    """Test that the agent correctly extracts date information"""
    response = run_async_test("Find trains from Mumbai to Pune on Friday")
    
    # Check date extraction (this will depend on your implementation)
    assert "date" in response, "Response should include a date field"
    assert response["date"], "Date should not be empty"
    
    # Basic date format check (YYYY-MM-DD)
    import re
    assert re.match(r"\d{4}-\d{2}-\d{2}", response["date"]), f"Date should be in YYYY-MM-DD format, got {response['date']}"
def test_train_structure():
    """Test that train objects have the correct structure"""
    response = run_async_test("Find trains from Delhi to Mumbai")
    
    # Skip test if no trains were found
    if not response.get("trains") or len(response["trains"]) == 0:
        pytest.skip("No trains found, skipping structure test")
    
    # Check first train structure
    train = response["trains"][0]
    required_train_keys = ["train_number", "train_name", "departure", "arrival", "duration", "availability", "fare"]
    for key in required_train_keys:
        assert key in train, f"Train object missing required key: {key}"
    
    # Check types
    assert isinstance(train["train_number"], str), "Train number should be a string"
    assert isinstance(train["train_name"], str), "Train name should be a string"
    assert isinstance(train["departure"], str), "Departure should be a string"
    assert isinstance(train["arrival"], str), "Arrival should be a string"
    assert isinstance(train["duration"], str), "Duration should be a string"
    assert isinstance(train["availability"], str), "Availability should be a string"
    assert isinstance(train["fare"], int), "Fare should be an integer"
# Main function to run tests manually if needed
if __name__ == "__main__":
    print("Running tests manually...")
    test_functions = [
        test_basic_query_structure,
        test_class_extraction,
        test_no_trains_route,
        test_date_extraction,
        test_train_structure
    ]
    
    results = []
    for test_func in test_functions:
        try:
            print(f"Running {test_func.__name__}...")
            test_func()
            results.append({"test": test_func.__name__, "status": "PASS"})
            print("✅ PASS")
        except Exception as e:
            results.append({"test": test_func.__name__, "status": "FAIL", "reason": str(e)})
            print(f"❌ FAIL: {str(e)}")
    
    # Print summary
    print("\n===== Test Results =====")
    for result in results:
        status = "✅ PASS" if result["status"] == "PASS" else f"❌ FAIL: {result['reason']}"
        print(f"{result['test']}: {status}")
    
    passes = sum(1 for r in results if r["status"] == "PASS")
    print(f"\nPassed {passes} out of {len(results)} tests")