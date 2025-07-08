import streamlit as st
import pandas as pd
import pandasql as psql
from openai import OpenAI
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="AI Data Analyst Demo",
    page_icon="📊",
    layout="wide"
)

FAVORITES_FILE = "data/favorites.json"

def load_favorites_from_file():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_favorites_to_file(favorites):
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Could not save favorites: {e}")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_name' not in st.session_state:
    st.session_state.df_name = None
if 'show_query_help' not in st.session_state:
    st.session_state.show_query_help = False
if 'show_schema' not in st.session_state:
    st.session_state.show_schema = False
if 'show_report' not in st.session_state:
    st.session_state.show_report = False
if 'edit_question' not in st.session_state:
    st.session_state.edit_question = None
if 'process_example' not in st.session_state:
    st.session_state.process_example = None
if 'favorites' not in st.session_state:
    st.session_state.favorites = load_favorites_from_file()
if 'run_favorite' not in st.session_state:
    st.session_state.run_favorite = None

def get_schema_info(df):
    """Generate schema information for the AI prompt"""
    schema_info = "Database Schema:\n"
    schema_info += f"Table name: 'df' (DataFrame)\n"
    schema_info += f"Number of rows: {len(df)}\n"
    schema_info += f"Number of columns: {len(df.columns)}\n\n"
    schema_info += "Columns:\n"
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        schema_info += f"- {col}: {dtype}, {null_count} null values, {unique_count} unique values\n"
    
    # Add sample data for context
    schema_info += f"\nSample data (first 3 rows):\n{df.head(3).to_string()}\n"
    
    return schema_info

def generate_sql_query(user_question, schema_info):
    """Use OpenAI to generate SQL query from natural language question"""
    
    # Load the system prompt from file
    try:
        with open("system_prompt.txt", "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        st.error("System prompt file not found. Using default prompt.")
        prompt_template = """
You are an expert SQL analyst. 

Given the following database schema and a user question, generate a SQL query to answer the question.

{schema_info}

User Question: {user_question}

Instructions:
1. Generate ONLY the SQL query, nothing else
2. Use the table name 'df' 
3. Make sure the query is valid and will execute successfully
4. For aggregation questions, use appropriate functions like COUNT(), SUM(), AVG(), etc.
5. For data quality questions, check for nulls, duplicates, outliers, etc.
6. Keep the query simple and focused on answering the question

SQL Query:
"""
    
    # Format the prompt with the actual data
    prompt = prompt_template.format(
        schema_info=schema_info,
        user_question=user_question
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert SQL analyst. Generate only SQL queries, no explanations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        sql_query = response.choices[0].message.content
        if sql_query:
            sql_query = sql_query.strip()
            # Clean up the response to get just the SQL
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            return sql_query.strip()
        return None
    
    except Exception as e:
        st.error(f"Error generating SQL query: {str(e)}")
        return None

def execute_query(sql_query, df):
    """Execute SQL query on the DataFrame using pandasql"""
    try:
        result = psql.sqldf(sql_query, locals())
        return result
    except Exception as e:
        error_msg = str(e)
        
        # Provide more helpful error messages
        if "syntax error" in error_msg.lower():
            if "transaction" in error_msg.lower():
                st.warning("💡 **Tip:** Column names with spaces need to be quoted. Try using `[Transaction Value]` or `'Transaction Value'` in your question.")
            else:
                st.warning("💡 **Tip:** There's a syntax error in the SQL. This might be due to column names with spaces or special characters.")
        elif "no such column" in error_msg.lower():
            st.warning("💡 **Tip:** The column name might not exist or might have spaces. Check the schema for exact column names.")
        elif "ambiguous column name" in error_msg.lower():
            st.warning("💡 **Tip:** Multiple columns have similar names. Be more specific about which column you want.")
        else:
            st.warning(f"💡 **Tip:** {error_msg}")
        
        return None

def format_result(result):
    """Format the query result for display"""
    if result is None or result.empty:
        return "No results found."
    
    # Check if this is a single count result (common for null checks, totals, etc.)
    if len(result) == 1 and len(result.columns) == 1:
        # Single value result
        value = result.iloc[0, 0]
        column_name = result.columns[0]
        return f"**Result:** {value}"
    
    # Check if this looks like a null count result (all numeric values in first row)
    elif len(result) == 1 and all(isinstance(val, (int, float)) for val in result.iloc[0]):
        # This is likely a count result - format it nicely
        result_text = "**Null Count Results:**\n\n"
        
        # Check if these are null counts (columns with "_nulls" suffix)
        null_columns = [col for col in result.columns if '_nulls' in col.lower()]
        if null_columns:
            # Format as null counts
            for col, val in result.iloc[0].items():
                if hasattr(val, 'item'):
                    val = val.item()
                # Clean up column name for display
                clean_name = col.replace('_nulls', '').replace('_', ' ').title()
                result_text += f"• **{clean_name}**: {val} null values\n"
        else:
            # Format as general counts
            for col, val in result.iloc[0].items():
                if hasattr(val, 'item'):
                    val = val.item()
                result_text += f"• **{col}**: {val}\n"
        
        return result_text
    
    # Check if this looks like a malformed result (all column names as headers)
    elif len(result) == 1 and len(result.columns) > 10 and all(str(val).isdigit() for val in result.iloc[0]):
        # This might be a malformed query result - try to interpret it as counts
        result_text = "**Results (interpreted as counts):**\n\n"
        for col, val in result.iloc[0].items():
            if hasattr(val, 'item'):
                val = val.item()
            result_text += f"• **{col}**: {val}\n"
        return result_text
    
    # Check if this is a null count result with multiple rows (one per column)
    elif len(result) > 1 and len(result.columns) == 1 and 'null_count' in str(result.columns[0]).lower():
        # This is likely a null count query that returned multiple rows
        result_text = "**Null Count Results:**\n\n"
        for i, (idx, row) in enumerate(result.iterrows()):
            val = row.iloc[0]
            if hasattr(val, 'item'):
                val = val.item()
            result_text += f"• **Column {i + 1}**: {val} null values\n"
        return result_text
    
    # Check if this is a simple count result with multiple rows
    elif len(result) > 1 and len(result.columns) == 1:
        # This might be a count query that returned multiple rows
        result_text = "**Count Results:**\n\n"
        for i, (idx, row) in enumerate(result.iterrows()):
            val = row.iloc[0]
            if hasattr(val, 'item'):
                val = val.item()
            result_text += f"• **Count {i + 1}**: {val}\n"
        return result_text
    
    else:
        # Regular table result - return the DataFrame object for Streamlit to render
        if len(result) <= 10:  # Show full table for small results
            return {"type": "table", "data": result, "message": f"**Results ({len(result)} rows):**"}
        else:  # Show first 10 rows for large results
            return {"type": "table", "data": result.head(10), "message": f"**Results ({len(result)} rows, showing first 10):**"}

def get_query_suggestions(user_question, error_type):
    """Get suggestions for improving the user question based on error type"""
    suggestions = []
    
    if "syntax error" in error_type.lower():
        suggestions.append("Try rephrasing your question to be more specific about column names")
        suggestions.append("Use simpler language and avoid complex conditions")
        suggestions.append("Mention the exact column name you want to analyze")
    
    elif "no such column" in error_type.lower():
        suggestions.append("Check the exact spelling of column names")
        suggestions.append("Use the 'Show Schema' button to see available columns")
        suggestions.append("Try using a different column name")
    
    elif "transaction" in error_type.lower():
        suggestions.append("Try: 'Show me transactions with values above 1000000'")
        suggestions.append("Try: 'What is the total Transaction Value?'")
        suggestions.append("Try: 'List the top 10 transactions by value'")
    
    else:
        suggestions.append("Try breaking down your question into simpler parts")
        suggestions.append("Use the example questions as a starting point")
        suggestions.append("Check the schema to understand the available data")
    
    return suggestions

def save_to_favorites(question, sql_query, result_summary):
    favorite = {
        "id": len(st.session_state.favorites) + 1,
        "question": question,
        "sql_query": sql_query,
        "result_summary": result_summary,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    for existing in st.session_state.favorites:
        if existing["question"] == question and existing["sql_query"] == sql_query:
            return False  # Already exists
    st.session_state.favorites.append(favorite)
    save_favorites_to_file(st.session_state.favorites)
    return True

def remove_from_favorites(favorite_id):
    st.session_state.favorites = [f for f in st.session_state.favorites if f["id"] != favorite_id]
    save_favorites_to_file(st.session_state.favorites)

def generate_developer_report(df, messages):
    """Generate a comprehensive developer report"""
    report = {}
    
    # Basic dataset info
    report['dataset_info'] = {
        'rows': len(df),
        'columns': len(df.columns),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
        'null_values_total': df.isnull().sum().sum(),
        'duplicate_rows': df.duplicated().sum()
    }
    
    # Column analysis
    column_analysis = []
    for col in df.columns:
        col_info = {
            'column_name': col,
            'data_type': str(df[col].dtype),
            'null_count': int(df[col].isnull().sum()),
            'null_percentage': round((df[col].isnull().sum() / len(df)) * 100, 2),
            'unique_count': int(df[col].nunique()),
            'unique_percentage': round((df[col].nunique() / len(df)) * 100, 2)
        }
        
        # Add sample values
        sample_values = df[col].dropna().head(5).tolist()
        col_info['sample_values'] = [str(v) for v in sample_values]
        
        # Add statistics for numeric columns
        if df[col].dtype in ['int64', 'float64']:
            col_info['min'] = float(df[col].min()) if not df[col].isnull().all() else None
            col_info['max'] = float(df[col].max()) if not df[col].isnull().all() else None
            col_info['mean'] = float(df[col].mean()) if not df[col].isnull().all() else None
            col_info['std'] = float(df[col].std()) if not df[col].isnull().all() else None
        
        column_analysis.append(col_info)
    
    report['column_analysis'] = column_analysis
    
    # Data quality metrics
    import numpy as np
    quality_metrics = {}
    
    # Missing values analysis
    missing_per_col = df.isnull().sum()
    quality_metrics['missing_values'] = {
        'total_missing': int(missing_per_col.sum()),
        'percentage_missing': round((missing_per_col.sum() / (len(df) * len(df.columns))) * 100, 2),
        'columns_with_missing': int((missing_per_col > 0).sum()),
        'missing_by_column': missing_per_col.to_dict()
    }
    
    # Duplicate analysis
    quality_metrics['duplicates'] = {
        'duplicate_rows': int(df.duplicated().sum()),
        'duplicate_percentage': round((df.duplicated().sum() / len(df)) * 100, 2)
    }
    
    # Outlier analysis for numeric columns
    outlier_analysis = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        if not df[col].isnull().all():
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers = (z_scores > 3).sum()
            outlier_analysis[col] = {
                'outlier_count': int(outliers),
                'outlier_percentage': round((outliers / len(df)) * 100, 2)
            }
    
    quality_metrics['outliers'] = outlier_analysis
    
    # Chat history analysis
    chat_analysis = {
        'total_messages': len(messages),
        'user_messages': len([m for m in messages if m['role'] == 'user']),
        'assistant_messages': len([m for m in messages if m['role'] == 'assistant']),
        'queries_with_sql': len([m for m in messages if m.get('sql_query')]),
        'failed_queries': len([m for m in messages if m.get('error')]),
        'successful_queries': len([m for m in messages if m.get('sql_query') and not m.get('error')])
    }
    
    # Extract SQL queries and their results
    sql_queries = []
    for msg in messages:
        if msg.get('sql_query'):
            sql_queries.append({
                'question': next((m['content'] for m in messages[:messages.index(msg)] if m['role'] == 'user'), 'Unknown'),
                'sql_query': msg['sql_query'],
                'success': not msg.get('error', False),
                'result_type': 'table' if isinstance(msg.get('content'), dict) and msg.get('content', {}).get('type') == 'table' else 'text'
            })
    
    report['quality_metrics'] = quality_metrics
    report['chat_analysis'] = chat_analysis
    report['sql_queries'] = sql_queries
    
    return report

# Main UI
st.title("🤖 AI Data Analyst Demo")
st.markdown("**Ask questions about your data in plain English!**")

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Data Upload")
    
    # Option to use sample data or upload file
    data_option = st.radio(
        "Choose data source:",
        ["Use Sample Data", "Upload CSV File"]
    )
    
    if data_option == "Use Sample Data":
        if st.button("Load Sample Data"):
            try:
                df = pd.read_csv("data/Data Dump - Accrual Accounts.csv")
                st.session_state.df = df
                st.session_state.df_name = "Sample Data (Accrual Accounts)"
                st.success("Sample data loaded successfully!")
            except Exception as e:
                st.error(f"Error loading sample data: {str(e)}")
    
    else:
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file to analyze"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.df = df
                st.session_state.df_name = uploaded_file.name
                st.success(f"File '{uploaded_file.name}' loaded successfully!")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    # Favorites section
    st.header("⭐ Favorites")
    
    if st.session_state.favorites:
        for favorite in st.session_state.favorites:
            with st.expander(f"💾 {favorite['question'][:50]}...", expanded=False):
                st.write(f"**Question:** {favorite['question']}")
                st.write(f"**Result:** {favorite['result_summary']}")
                st.write(f"**Saved:** {favorite['timestamp']}")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("🔄 Run Again", key=f"run_fav_{favorite['id']}"):
                        st.session_state.run_favorite = favorite['question']
                        st.rerun()
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_fav_{favorite['id']}"):
                        remove_from_favorites(favorite['id'])
                        st.rerun()
                
                with st.expander("🔍 View SQL"):
                    st.code(favorite['sql_query'], language="sql")
    else:
        st.info("No favorites yet. Save queries you like to see them here!")

# Main chat interface
if st.session_state.df is not None:
    st.header(f"📊 Analyzing: {st.session_state.df_name}")
    
    # Display data info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", len(st.session_state.df))
    with col2:
        st.metric("Columns", len(st.session_state.df.columns))
    with col3:
        st.metric("Memory Usage", f"{st.session_state.df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    with col4:
        null_count = st.session_state.df.isnull().sum().sum()
        st.metric("Null Values", null_count)
    
    # Data Quality Dashboard Button
    if st.button("🧪 Generate Data Quality Dashboard", key="dq_dashboard_btn"):
        df = st.session_state.df
        dq_report = {}
        # Missing values
        missing_per_col = df.isnull().sum()
        total_missing = missing_per_col.sum()
        percent_missing = (total_missing / (df.shape[0] * df.shape[1])) * 100
        dq_report['missing'] = missing_per_col
        dq_report['total_missing'] = total_missing
        dq_report['percent_missing'] = percent_missing
        # Duplicates
        duplicate_rows = df.duplicated().sum()
        dq_report['duplicates'] = duplicate_rows
        percent_duplicates = (duplicate_rows / df.shape[0]) * 100 if df.shape[0] > 0 else 0
        dq_report['percent_duplicates'] = percent_duplicates
        # Outliers (z-score > 3 or < -3 for numeric columns)
        import numpy as np
        outlier_counts = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            col_z = (df[col] - df[col].mean()) / df[col].std(ddof=0)
            outliers = ((col_z > 3) | (col_z < -3)).sum()
            outlier_counts[col] = int(outliers)
        dq_report['outliers'] = outlier_counts
        total_outliers = sum(outlier_counts.values())
        dq_report['total_outliers'] = total_outliers
        percent_outliers = (total_outliers / (df.shape[0] * max(1, len(outlier_counts)))) * 100 if len(outlier_counts) > 0 else 0
        dq_report['percent_outliers'] = percent_outliers
        # Data Quality Score (simple formula: 100 - weighted sum of issues)
        score = 100 - (percent_missing * 0.5 + percent_duplicates * 0.3 + percent_outliers * 0.2)
        score = max(0, min(100, round(score, 1)))
        dq_report['score'] = score
        st.session_state.dq_report = dq_report
        st.session_state.show_dq_dashboard = True
        st.rerun()

    # Show Data Quality Dashboard if requested
    if st.session_state.get('show_dq_dashboard', False) and st.session_state.get('dq_report', None):
        dq = st.session_state.dq_report
        st.subheader('🧪 Data Quality Dashboard')
        # Score visual
        if dq['score'] >= 90:
            emoji = '🟢'
        elif dq['score'] >= 70:
            emoji = '🟡'
        else:
            emoji = '🔴'
        st.markdown(f"### {emoji} Data Quality Score: **{dq['score']} / 100**")
        st.progress(dq['score'] / 100)
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Missing Values", f"{dq['total_missing']}", delta=f"{dq['percent_missing']:.2f}%")
        with col2:
            st.metric("Duplicate Rows", f"{dq['duplicates']}", delta=f"{dq['percent_duplicates']:.2f}%")
        with col3:
            st.metric("Outliers (numeric)", f"{dq['total_outliers']}", delta=f"{dq['percent_outliers']:.2f}%")
        # Missing values per column
        st.markdown("#### Missing Values by Column")
        missing_df = dq['missing'].to_frame('Missing Count')
        missing_df = missing_df[missing_df['Missing Count'] != 0]
        st.dataframe(missing_df)
        # Outliers per column
        if dq['outliers']:
            st.markdown("#### Outliers by Numeric Column")
            outlier_df = pd.DataFrame.from_dict(dq['outliers'], orient='index').reset_index()
            outlier_df.columns = ["Column", "Outlier Count"]
            outlier_df = outlier_df[outlier_df["Outlier Count"] != 0]
            st.dataframe(outlier_df)
        # Hide dashboard button
        if st.button("❌ Close Data Quality Dashboard", key="close_dq_dashboard"):
            st.session_state.show_dq_dashboard = False
            st.rerun()

    # Chat interface
    st.subheader("💬 Ask Questions About Your Data")
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.write(message["content"])
            else:
                # Handle different content types
                content = message["content"]
                if isinstance(content, dict) and content.get("type") == "table":
                    st.markdown(content["message"])
                    st.dataframe(content["data"], use_container_width=True)
                else:
                    st.write(content)
                
                if "sql_query" in message:
                    with st.expander("🔍 View SQL Query"):
                        st.code(message["sql_query"], language="sql")
                    # Add Save to Favorites button for this assistant message
                    # Find the previous user message for the question
                    user_question = None
                    for prev in reversed(st.session_state.messages[:idx]):
                        if prev["role"] == "user":
                            user_question = prev["content"]
                            break
                    if user_question:
                        if st.button("⭐ Save to Favorites", key=f"save_fav_{idx}"):
                            # Create a summary of the result
                            if isinstance(content, dict) and content.get("type") == "table":
                                result_summary = f"Table with {len(content['data'])} rows"
                            else:
                                result_summary = str(content)[:100] + "..." if len(str(content)) > 100 else str(content)
                            if save_to_favorites(user_question, message["sql_query"], result_summary):
                                st.success("✅ Query saved to favorites!")
                            else:
                                st.warning("⚠️ This query is already in your favorites!")
                            st.rerun()
    
    # Chat input
    if st.session_state.edit_question is not None:
        # Show the question for editing with a text input
        st.info("✏️ **Edit your question:**")
        edited_question = st.text_input("Modify your question:", value=st.session_state.edit_question, key="edit_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("✅ Send", key="send_edited"):
                if edited_question and edited_question.strip():
                    # Add the edited question to chat and process it
                    prompt = edited_question.strip()
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.edit_question = None  # Clear the edit question
                    st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_edit"):
                st.session_state.edit_question = None
                st.rerun()
    else:
        # Regular chat input
        prompt = st.chat_input("Ask a question about your data...")
        
        if prompt:
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
    
        # Process any pending question (from chat input, edit, or example)
    prompt_to_process = None
    
    if 'prompt' in locals() and prompt:
        prompt_to_process = prompt.strip()
    elif st.session_state.edit_question is not None and 'edited_question' in locals() and edited_question:
        prompt_to_process = edited_question.strip()
    elif hasattr(st.session_state, 'process_example') and st.session_state.process_example:
        prompt_to_process = st.session_state.process_example.strip()
        # Clear the example flag after processing
        st.session_state.process_example = None
    elif hasattr(st.session_state, 'run_favorite') and st.session_state.run_favorite:
        prompt_to_process = st.session_state.run_favorite.strip()
        # Clear the favorite flag after processing
        st.session_state.run_favorite = None
    
    if prompt_to_process:
        # Generate and execute SQL query
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your data..."):
                # Get schema information
                schema_info = get_schema_info(st.session_state.df)
                
                # Generate SQL query
                sql_query = generate_sql_query(prompt_to_process, schema_info)
                
                if sql_query:
                    # Execute query
                    result = execute_query(sql_query, st.session_state.df)
                    
                    if result is not None:
                        # Format and display result
                        formatted_result = format_result(result)
                        
                        # Handle different result types
                        if isinstance(formatted_result, dict) and formatted_result.get("type") == "table":
                            # Display table result
                            st.markdown(formatted_result["message"])
                            st.dataframe(formatted_result["data"], use_container_width=True)
                            
                            # Add assistant message to chat
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": formatted_result,
                                "sql_query": sql_query
                            })
                        else:
                            # Display text result
                            st.write(formatted_result)
                            
                            # Add assistant message to chat
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": formatted_result,
                                "sql_query": sql_query
                            })
                        
                        # Add Save to Favorites button
                        if st.button("⭐ Save to Favorites", key=f"save_fav_{len(st.session_state.messages)}"):
                            # Create a summary of the result
                            if isinstance(formatted_result, dict) and formatted_result.get("type") == "table":
                                result_summary = f"Table with {len(formatted_result['data'])} rows"
                            else:
                                result_summary = str(formatted_result)[:100] + "..." if len(str(formatted_result)) > 100 else str(formatted_result)
                            
                            if save_to_favorites(prompt_to_process, sql_query, result_summary):
                                st.success("✅ Query saved to favorites!")
                            else:
                                st.warning("⚠️ This query is already in your favorites!")
                            st.rerun()
                    else:
                        # Handle query execution error gracefully
                        error_message = "❌ **Query Execution Failed**\n\n"
                        error_message += "The generated SQL query couldn't be executed. This might be due to:\n"
                        error_message += "• Column names with spaces or special characters\n"
                        error_message += "• Invalid SQL syntax\n"
                        error_message += "• Data type mismatches\n\n"
                        
                        # Show the problematic SQL
                        error_message += f"**Generated SQL:**\n```sql\n{sql_query}\n```\n\n"
                        
                        # Get suggestions based on the error
                        suggestions = get_query_suggestions(prompt_to_process, "syntax error")
                        if suggestions:
                            error_message += "**💡 Suggestions:**\n"
                            for suggestion in suggestions:
                                error_message += f"• {suggestion}\n"
                            error_message += "\n"
                        
                        # Add retry and help options
                        error_message += "**What would you like to do?**\n"
                        error_message += "1. **Retry** - Try generating a new SQL query\n"
                        error_message += "2. **Modify Question** - Rephrase your question\n"
                        error_message += "3. **Show Data Schema** - See available columns and data types"
                        
                        st.markdown(error_message)
                        
                        # Add interactive buttons for error recovery
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("🔄 Retry", key=f"retry_{len(st.session_state.messages)}"):
                                # Remove the failed assistant message and retry the last user question
                                if st.session_state.messages:
                                    # Find and remove the last assistant message (the failed one)
                                    for i in range(len(st.session_state.messages) - 1, -1, -1):
                                        if st.session_state.messages[i]["role"] == "assistant":
                                            st.session_state.messages.pop(i)
                                            break
                                st.rerun()
                        
                        with col2:
                            if st.button("✏️ Modify Question", key=f"modify_{len(st.session_state.messages)}"):
                                # Find the last user question and set it for editing
                                if st.session_state.messages:
                                    for i in range(len(st.session_state.messages) - 1, -1, -1):
                                        if st.session_state.messages[i]["role"] == "user":
                                            last_question = st.session_state.messages[i]["content"]
                                            st.session_state.edit_question = last_question
                                            break
                                st.session_state.show_query_help = True
                                st.rerun()

                        
                        with col3:
                            if st.button("📊 Generate Report", key=f"report_{len(st.session_state.messages)}"):
                                st.session_state.show_report = True
                                st.rerun()
     
                        
                        # Add assistant message to chat
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_message,
                            "sql_query": sql_query,
                            "error": True
                        })
                else:
                    st.error("Failed to generate SQL query. Please try rephrasing your question.")
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "Sorry, I couldn't understand your question. Please try rephrasing it."
                    })
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Help interfaces
    if st.session_state.show_query_help:
        st.subheader("✏️ Query Modification Help")
        st.markdown("""
        **Tips for better questions:**
        
        ✅ **Good examples:**
        - "Show me transactions with values above 1000000"
        - "What is the total amount in the Transaction Value column?"
        - "How many records have null values in the Currency column?"
        - "List the top 10 transactions by value"
        
        ❌ **Avoid:**
        - Column names with spaces (use quotes or brackets)
        - Vague descriptions
        - Complex multi-step questions
        
        **Column names in this dataset:**
        """)
        
        # Show column names with data types
        col_info = []
        for col in st.session_state.df.columns:
            dtype = str(st.session_state.df[col].dtype)
            null_count = st.session_state.df[col].isnull().sum()
            col_info.append(f"• **{col}** ({dtype}) - {null_count} null values")
        
        st.markdown("\n".join(col_info))
        
        if st.button("✅ Got it, close help"):
            st.session_state.show_query_help = False
            st.rerun()
    
    if st.session_state.show_report:
        # Generate the comprehensive report
        report = generate_developer_report(st.session_state.df, st.session_state.messages)
        
        st.subheader("📊 Developer Report")
        st.markdown("### Comprehensive Analysis Report")
        
        # Dataset Overview
        st.markdown("#### 📈 Dataset Overview")
        info = report['dataset_info']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{info['rows']:,}")
        with col2:
            st.metric("Total Columns", info['columns'])
        with col3:
            st.metric("Memory Usage", f"{info['memory_usage_mb']:.2f} MB")
        with col4:
            st.metric("Duplicate Rows", info['duplicate_rows'])
        
        # Data Quality Summary
        st.markdown("#### 🔍 Data Quality Analysis")
        qm = report['quality_metrics']
        
        # Missing values summary
        missing_info = qm['missing_values']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Missing Values", missing_info['total_missing'])
        with col2:
            st.metric("Missing Percentage", f"{missing_info['percentage_missing']:.2f}%")
        with col3:
            st.metric("Columns with Missing", missing_info['columns_with_missing'])
        
        # Duplicates and outliers
        dup_info = qm['duplicates']
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Duplicate Rows", dup_info['duplicate_rows'], delta=f"{dup_info['duplicate_percentage']:.2f}%")
        with col2:
            total_outliers = sum(qm['outliers'].values()) if qm['outliers'] else 0
            st.metric("Total Outliers", total_outliers)
        
        # Column Analysis
        st.markdown("#### 📋 Column Analysis")
        col_df = pd.DataFrame(report['column_analysis'])
        st.dataframe(col_df, use_container_width=True)
        
        # Chat Analysis
        st.markdown("#### 💬 Chat Session Analysis")
        chat_info = report['chat_analysis']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Messages", chat_info['total_messages'])
        with col2:
            st.metric("User Questions", chat_info['user_messages'])
        with col3:
            st.metric("Successful Queries", chat_info['successful_queries'])
        with col4:
            st.metric("Failed Queries", chat_info['failed_queries'])
        
        # SQL Queries Summary
        if report['sql_queries']:
            st.markdown("#### 🔍 SQL Queries Executed")
            sql_df = pd.DataFrame(report['sql_queries'])
            st.dataframe(sql_df, use_container_width=True)
        
        # Export options
        st.markdown("#### 📤 Export Options")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Export Report as JSON"):
                import json
                report_json = json.dumps(report, indent=2, default=str)
                st.download_button(
                    label="📥 Download JSON Report",
                    data=report_json,
                    file_name=f"developer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        with col2:
            if st.button("📊 Export Column Analysis as CSV"):
                col_df_csv = col_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=col_df_csv,
                    file_name=f"column_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        if st.button("❌ Close Report"):
            st.session_state.show_report = False
            st.rerun()
    
    # Example questions
    st.subheader("💡 Example Questions You Can Ask")
    example_questions = [
        "How many rows are in the dataset?",
        "What are the column names?",
        "How many null values are in each column?",
        "What is the total transaction value?",
        "Show me the top 5 transactions by value",
        "What is the average transaction value?",
        "How many transactions are there per fiscal year?",
        "What are the unique business transaction types?",
        "Show me transactions with values greater than 1000000",
        "What is the distribution of debit vs credit transactions?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(example_questions):
        with cols[i % 2]:
            if st.button(question, key=f"example_{i}"):
                # Add the question to chat and process it immediately
                st.session_state.messages.append({"role": "user", "content": question})
                # Set a flag to process this example question
                st.session_state.process_example = question
                st.rerun()

else:
    st.info("👈 Please upload a CSV file or load sample data from the sidebar to start analyzing!")
    
    # Show sample data preview
    st.subheader("📋 Sample Data Preview")
    try:
        sample_df = pd.read_csv("data/Data Dump - Accrual Accounts.csv", nrows=5)
        st.dataframe(sample_df)
        st.caption("This is a preview of the sample data. Load it to start asking questions!")
    except:
        st.warning("Sample data file not found. Please upload a CSV file to get started.")

# Footer
st.markdown("---")
st.markdown("*Powered by OpenAI GPT-4o-mini and Streamlit*") 