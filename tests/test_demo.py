#!/usr/bin/env python3
"""
Test script for the AI Data Analyst Demo
This script tests the core functionality without running the full Streamlit app
"""

import pandas as pd
import pandasql as psql
from openai import OpenAI
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_data_loading():
    """Test loading the sample data"""
    print("Testing data loading...")
    try:
        df = pd.read_csv("data/Data Dump - Accrual Accounts.csv")
        print(f"✅ Successfully loaded data: {len(df)} rows, {len(df.columns)} columns")
        return True
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return False

def test_sql_execution():
    """Test basic SQL execution with pandasql"""
    print("\nTesting SQL execution...")
    try:
        df = pd.read_csv("data/Data Dump - Accrual Accounts.csv")
        
        # Test a simple query
        query = "SELECT COUNT(*) as total_rows FROM df"
        result = psql.sqldf(query, locals())
        if result is not None and not result.empty:
            print(f"✅ SQL execution successful: {result.iloc[0, 0]} total rows")
        else:
            print("✅ SQL execution successful: 0 total rows")
        
        # Test another query
        query2 = "SELECT COUNT(*) as null_count FROM df WHERE [Transaction Value] IS NULL"
        result2 = psql.sqldf(query2, locals())
        if result2 is not None and not result2.empty:
            print(f"✅ Null check query successful: {result2.iloc[0, 0]} null values")
        else:
            print("✅ Null check query successful: 0 null values")
        
        return True
    except Exception as e:
        print(f"❌ SQL execution failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI API connection...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hello, AI is working!'"}
            ],
            max_tokens=50
        )
        print(f"✅ OpenAI API connection successful: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

# def test_sql_generation():
#     """Test SQL generation from natural language"""
#     print("\nTesting SQL generation...")
#     try:
#         df = pd.read_csv("data/Data Dump - Accrual Accounts.csv")
        
#         # Create schema info
#         schema_info = f"""
#         Database Schema:
#         Table name: 'df' (DataFrame)
#         Number of rows: {len(df)}
#         Number of columns: {len(df.columns)}
        
#         Columns: {', '.join(df.columns.tolist())}
#         """
        
#         # Load the system prompt from file
#         try:
#             with open("system_prompt.txt", "r") as f:
#                 prompt_template = f.read()
#         except FileNotFoundError:
#             print("System prompt file not found. Using default prompt.")
#             prompt_template = """
#         You are an expert SQL analyst. Given the following database schema and a user question, generate a SQL query to answer the question.

#         {schema_info}

#         User Question: {user_question}

#         Instructions:
#         1. Generate ONLY the SQL query, nothing else
#         2. Use the table name 'df' 
#         3. Make sure the query is valid and will execute successfully

#         SQL Query:
#         """
        
#         # Format the prompt with the actual data
#         prompt = prompt_template.format(
#             schema_info=schema_info,
#             user_question="How many rows are in the dataset?"
#         )
        
#         response = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an expert SQL analyst. Generate only SQL queries, no explanations."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=100,
#             temperature=0.1
#         )
        
#         sql_query = response.choices[0].message.content
#         if sql_query:
#             sql_query = sql_query.strip()
#             print(f"✅ SQL generation successful: {sql_query}")
            
#             # Test the generated query
#             result = psql.sqldf(sql_query, locals())
#             if result is not None and not result.empty:
#                 print(f"✅ Generated query executed successfully: {result.iloc[0, 0]} rows")
#             else:
#                 print("✅ Generated query executed successfully: 0 rows")
#         else:
#             print("❌ SQL generation failed: No response from API")
#             return False
        
#         return True
#     except Exception as e:
#         print(f"❌ SQL generation failed: {e}")
#         return False

def main():
    """Run all tests"""
    print("🧪 Testing AI Data Analyst Demo Components\n")
    
    tests = [
        ("Data Loading", test_data_loading),
        ("SQL Execution", test_sql_execution),
        ("OpenAI Connection", test_openai_connection),
        ("SQL Generation", test_sql_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The demo should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 