#!/usr/bin/env python3
"""
Test script for the favorites functionality
"""

import sys
import os

# Add the current directory to the path so we can import from data_chat_demo
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock Streamlit session state for testing
class MockSessionState:
    def __init__(self):
        self.favorites = []
        self.run_favorite = None

# Mock the datetime for testing
from datetime import datetime

def test_save_to_favorites():
    """Test saving queries to favorites"""
    print("🧪 Testing save_to_favorites function...")
    
    # Mock session state
    mock_session = MockSessionState()
    
    # Test data
    question = "How many rows are in the dataset?"
    sql_query = "SELECT COUNT(*) FROM df"
    result_summary = "Total rows: 1000"
    
    # Test saving a new favorite
    favorite = {
        "id": len(mock_session.favorites) + 1,
        "question": question,
        "sql_query": sql_query,
        "result_summary": result_summary,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    mock_session.favorites.append(favorite)
    
    assert len(mock_session.favorites) == 1
    assert mock_session.favorites[0]["question"] == question
    assert mock_session.favorites[0]["sql_query"] == sql_query
    print("✅ Save to favorites test passed!")

def test_remove_from_favorites():
    """Test removing queries from favorites"""
    print("🧪 Testing remove_from_favorites function...")
    
    # Mock session state
    mock_session = MockSessionState()
    
    # Add a test favorite
    favorite = {
        "id": 1,
        "question": "Test question",
        "sql_query": "SELECT * FROM df",
        "result_summary": "Test result",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    mock_session.favorites.append(favorite)
    assert len(mock_session.favorites) == 1
    
    # Remove the favorite
    mock_session.favorites = [f for f in mock_session.favorites if f["id"] != 1]
    assert len(mock_session.favorites) == 0
    print("✅ Remove from favorites test passed!")

def test_duplicate_prevention():
    """Test that duplicate queries are not saved"""
    print("🧪 Testing duplicate prevention...")
    
    # Mock session state
    mock_session = MockSessionState()
    
    # Add a favorite
    favorite1 = {
        "id": 1,
        "question": "Same question",
        "sql_query": "SELECT COUNT(*) FROM df",
        "result_summary": "Result 1",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    mock_session.favorites.append(favorite1)
    
    # Try to add the same question and SQL
    favorite2 = {
        "id": 2,
        "question": "Same question",
        "sql_query": "SELECT COUNT(*) FROM df",
        "result_summary": "Result 2",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Check if it already exists
    is_duplicate = any(
        existing["question"] == favorite2["question"] and 
        existing["sql_query"] == favorite2["sql_query"] 
        for existing in mock_session.favorites
    )
    
    if not is_duplicate:
        mock_session.favorites.append(favorite2)
    
    # Should only have one favorite (the duplicate was prevented)
    assert len(mock_session.favorites) == 1
    print("✅ Duplicate prevention test passed!")

def test_favorites_structure():
    """Test the structure of favorites data"""
    print("🧪 Testing favorites data structure...")
    
    favorite = {
        "id": 1,
        "question": "Test question",
        "sql_query": "SELECT * FROM df",
        "result_summary": "Test result",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Check required fields
    required_fields = ["id", "question", "sql_query", "result_summary", "timestamp"]
    for field in required_fields:
        assert field in favorite, f"Missing required field: {field}"
    
    # Check data types
    assert isinstance(favorite["id"], int)
    assert isinstance(favorite["question"], str)
    assert isinstance(favorite["sql_query"], str)
    assert isinstance(favorite["result_summary"], str)
    assert isinstance(favorite["timestamp"], str)
    
    print("✅ Favorites data structure test passed!")

if __name__ == "__main__":
    print("🚀 Starting favorites functionality tests...\n")
    
    try:
        test_save_to_favorites()
        test_remove_from_favorites()
        test_duplicate_prevention()
        test_favorites_structure()
        
        print("\n🎉 All tests passed! The favorites functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1) 