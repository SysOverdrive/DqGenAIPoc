#!/usr/bin/env python3
"""
Test script for the improved result formatting in the AI Data Analyst Demo
"""

import pandas as pd
import pandasql as psql

def test_formatting():
    """Test the improved result formatting"""
    print("🧪 Testing Result Formatting Improvements\n")
    
    # Load sample data
    try:
        df = pd.read_csv("data/Data Dump - Accrual Accounts.csv")
        print(f"✅ Loaded data: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # Test different types of queries and their formatting
    test_queries = [
        ("Simple count", "SELECT COUNT(*) as total_rows FROM df"),
        ("Null check", "SELECT COUNT(*) as null_count FROM df WHERE [Transaction Value] IS NULL"),
        ("Top 5 results", "SELECT * FROM df ORDER BY [Transaction Value] DESC LIMIT 5"),
        ("Single value", "SELECT AVG([Transaction Value]) as avg_value FROM df"),
        ("Multiple counts", "SELECT COUNT(*) as total, COUNT([Transaction Value]) as non_null FROM df")
    ]
    
    print("\n🔍 Testing different query types and formatting:")
    
    for query_name, query in test_queries:
        print(f"\n📊 {query_name}:")
        print(f"   SQL: {query}")
        
        try:
            result = psql.sqldf(query, locals())
            if result is not None and not result.empty:
                print(f"   ✅ Success: {len(result)} rows, {len(result.columns)} columns")
                
                # Test our formatting logic
                if len(result) == 1 and len(result.columns) == 1:
                    print(f"   📝 Single value result: {result.iloc[0, 0]}")
                elif len(result) == 1 and all(isinstance(val, (int, float)) for val in result.iloc[0]):
                    print(f"   📝 Count result: {dict(result.iloc[0])}")
                else:
                    print(f"   📝 Table result: {len(result)} rows")
            else:
                print(f"   ⚠️  No results returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Formatting test completed!")

if __name__ == "__main__":
    test_formatting() 