#!/usr/bin/env python3
"""
Test script for null count formatting in the AI Data Analyst Demo
"""

import pandas as pd
import pandasql as psql

def test_null_count_formatting():
    """Test the null count result formatting"""
    print("🧪 Testing Null Count Formatting\n")
    
    # Load sample data
    try:
        df = pd.read_csv("data/Data Dump - Accrual Accounts.csv")
        print(f"✅ Loaded data: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # Test the problematic query that returns multiple rows
    problematic_query = """
    SELECT COUNT(*) as null_count FROM df WHERE [Unnamed: 0] IS NULL
    UNION ALL
    SELECT COUNT(*) as null_count FROM df WHERE [Authorization Group] IS NULL
    UNION ALL
    SELECT COUNT(*) as null_count FROM df WHERE [Bus. Transac. Type] IS NULL
    UNION ALL
    SELECT COUNT(*) as null_count FROM df WHERE [Calculate Tax] IS NULL
    UNION ALL
    SELECT COUNT(*) as null_count FROM df WHERE [Cash Flow-Relevant Doc.] IS NULL
    """
    
    print(f"\n🔍 Testing problematic null count query:")
    print(f"SQL: {problematic_query}")
    
    try:
        result = psql.sqldf(problematic_query, locals())
        if result is not None and not result.empty:
            print(f"✅ Query executed: {len(result)} rows, {len(result.columns)} columns")
            
            # Test our formatting logic
            if len(result) > 1 and len(result.columns) == 1 and 'null_count' in str(result.columns[0]).lower():
                print("📝 Detected as null count result with multiple rows")
                result_text = "**Null Count Results:**\n\n"
                for i, (idx, row) in enumerate(result.iterrows()):
                    val = row.iloc[0]
                    if hasattr(val, 'item'):
                        val = val.item()
                    result_text += f"• **Column {i + 1}**: {val} null values\n"
                print(result_text)
            else:
                print("📝 Not detected as null count result")
                print(result)
        else:
            print("⚠️  No results returned")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test a better query that returns one row
    better_query = """
    SELECT 
        SUM(CASE WHEN [Unnamed: 0] IS NULL THEN 1 ELSE 0 END) as unnamed_nulls,
        SUM(CASE WHEN [Authorization Group] IS NULL THEN 1 ELSE 0 END) as auth_nulls,
        SUM(CASE WHEN [Bus. Transac. Type] IS NULL THEN 1 ELSE 0 END) as bus_type_nulls,
        SUM(CASE WHEN [Calculate Tax] IS NULL THEN 1 ELSE 0 END) as tax_nulls,
        SUM(CASE WHEN [Cash Flow-Relevant Doc.] IS NULL THEN 1 ELSE 0 END) as cash_flow_nulls
    FROM df
    """
    
    print(f"\n🔍 Testing better null count query:")
    print(f"SQL: {better_query}")
    
    try:
        result = psql.sqldf(better_query, locals())
        if result is not None and not result.empty:
            print(f"✅ Query executed: {len(result)} rows, {len(result.columns)} columns")
            
            # Test our formatting logic
            if len(result) == 1 and all(isinstance(val, (int, float)) for val in result.iloc[0]):
                print("📝 Detected as count result with single row")
                result_text = "**Results:**\n\n"
                for col, val in result.iloc[0].items():
                    if hasattr(val, 'item'):
                        val = val.item()
                    result_text += f"• **{col}**: {val}\n"
                print(result_text)
            else:
                print("📝 Not detected as count result")
                print(result)
        else:
            print("⚠️  No results returned")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Null count formatting test completed!")

if __name__ == "__main__":
    test_null_count_formatting() 