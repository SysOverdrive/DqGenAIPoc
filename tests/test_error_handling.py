#!/usr/bin/env python3
"""
Test script for the improved error handling in the AI Data Analyst Demo
"""

import pandas as pd
import pandasql as psql
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_error_handling():
    """Test the error handling with problematic queries"""
    print("🧪 Testing Error Handling Improvements\n")
    
    # Load sample data
    try:
        df = pd.read_csv("data/Data Dump - Accrual Accounts.csv")
        print(f"✅ Loaded data: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # Test problematic queries
    problematic_queries = [
        "SELECT * FROM df WHERE Transaction Value > 1000000",  # Column with space
        "SELECT * FROM df WHERE nonexistent_column = 'test'",  # Non-existent column
        "SELECT COUNT(*) FROM df WHERE 'Transaction Value' IS NULL",  # Quoted column
        "SELECT * FROM df WHERE [Transaction Value] > 1000000"  # Bracket notation
    ]
    
    print("\n🔍 Testing problematic SQL queries:")
    
    for i, query in enumerate(problematic_queries, 1):
        print(f"\n{i}. Testing: {query}")
        try:
            result = psql.sqldf(query, locals())
            if result is not None and not result.empty:
                print(f"   ✅ Success: {len(result)} rows returned")
            else:
                print(f"   ⚠️  No results returned")
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}")
            
            # Test our error handling logic
            if "syntax error" in error_msg.lower():
                if "transaction" in error_msg.lower():
                    print("   💡 Tip: Column names with spaces need to be quoted")
                else:
                    print("   💡 Tip: There's a syntax error in the SQL")
            elif "no such column" in error_msg.lower():
                print("   💡 Tip: The column name might not exist")
    
    print("\n✅ Error handling test completed!")

if __name__ == "__main__":
    test_error_handling() 