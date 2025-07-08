#!/usr/bin/env python3
"""
Test script for improved null count handling in the AI Data Analyst Demo
"""

import pandas as pd
import pandasql as psql

def test_null_count_improvements():
    """Test the improved null count result formatting"""
    print("🧪 Testing Improved Null Count Handling\n")
    
    # Load sample data
    try:
        df = pd.read_csv("data/Data Dump - Accrual Accounts.csv")
        print(f"✅ Loaded data: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # Test different null count queries
    test_queries = [
        ("Simple null count", "SELECT COUNT(*) as null_count FROM df WHERE [Transaction Value] IS NULL"),
        ("Multiple column nulls", """
            SELECT 
                SUM(CASE WHEN [Transaction Value] IS NULL THEN 1 ELSE 0 END) as transaction_value_nulls,
                SUM(CASE WHEN [Currency] IS NULL THEN 1 ELSE 0 END) as currency_nulls,
                SUM(CASE WHEN [Country Key] IS NULL THEN 1 ELSE 0 END) as country_key_nulls
            FROM df
        """),
        ("Alternative approach", """
            SELECT 
                COUNT(*) as total_rows,
                COUNT([Transaction Value]) as transaction_value_non_null,
                COUNT([Currency]) as currency_non_null
            FROM df
        """)
    ]
    
    print("\n🔍 Testing different null count approaches:")
    
    for query_name, query in test_queries:
        print(f"\n📊 {query_name}:")
        print(f"   SQL: {query.strip()}")
        
        try:
            result = psql.sqldf(query, locals())
            if result is not None and not result.empty:
                print(f"   ✅ Success: {len(result)} rows, {len(result.columns)} columns")
                
                # Test our formatting logic
                if len(result) == 1 and all(isinstance(val, (int, float)) for val in result.iloc[0]):
                    print("   📝 Detected as count result with single row")
                    
                    # Check if these are null counts
                    null_columns = [col for col in result.columns if '_nulls' in col.lower()]
                    if null_columns:
                        print("   📝 Formatting as null counts:")
                        for col, val in result.iloc[0].items():
                            if hasattr(val, 'item'):
                                val = val.item()
                            clean_name = col.replace('_nulls', '').replace('_', ' ').title()
                            print(f"      • {clean_name}: {val} null values")
                    else:
                        print("   📝 Formatting as general counts:")
                        for col, val in result.iloc[0].items():
                            if hasattr(val, 'item'):
                                val = val.item()
                            print(f"      • {col}: {val}")
                else:
                    print("   📝 Not detected as count result")
                    print(result)
            else:
                print("   ⚠️  No results returned")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Null count improvements test completed!")

if __name__ == "__main__":
    test_null_count_improvements() 