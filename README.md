# 🤖 AI Data Analyst Demo

A Streamlit application that demonstrates how AI can be used as a "data analyst" to answer questions about data in plain English.

## Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **AI-Powered SQL Generation**: Uses OpenAI GPT-4o-mini to convert questions into SQL queries
- **Interactive Chat Interface**: Chat-like experience for data exploration
- **File Upload Support**: Upload your own CSV files or use the provided sample data
- **Real-time Analysis**: Get instant answers to data questions
- **SQL Query Visibility**: See the generated SQL queries for transparency
- **Graceful Error Handling**: When queries fail, get helpful suggestions and recovery options
- **Query Modification Help**: Interactive help to improve your questions
- **Data Schema Viewer**: See column names, data types, and sample values
- **Retry Functionality**: Easily retry failed queries with one click - generates a new SQL query for the same question

## Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (included in the demo)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   streamlit run data_chat_demo.py
   ```

3. **Open your browser** and navigate to the URL shown in the terminal (usually http://localhost:8501)

## How to Use

1. **Load Data**: 
   - Use the sidebar to either load the sample data or upload your own CSV file
   - The sample data contains financial transaction records

2. **Ask Questions**: 
   - Type questions in the chat interface
   - Use the example questions as a starting point
   - The AI will generate SQL queries and return results

3. **Explore Results**:
   - View the generated SQL queries by clicking "View SQL Query"
   - Results are displayed in a user-friendly format
   - Clear the chat anytime to start fresh

## Example Questions

- "How many rows are in the dataset?"
- "What is the total transaction value?"
- "Show me the top 5 transactions by value"
- "How many null values are in each column?"
- "What is the average transaction value?"
- "How many transactions are there per fiscal year?"
- "What are the unique business transaction types?"

## Error Handling

When a query fails to execute, the app provides:

1. **Clear Error Messages**: Explains what went wrong
2. **Generated SQL Display**: Shows the problematic query
3. **Helpful Suggestions**: Tips to improve your question
4. **Recovery Options**:
   - **Retry**: Generate a new SQL query
   - **Modify Question**: Get help rephrasing your question
   - **Show Schema**: View available columns and data types

**Common Issues & Solutions:**
- **Column names with spaces**: Use quotes or brackets in your question
- **Non-existent columns**: Check the schema for exact column names
- **Syntax errors**: Simplify your question or use the help interface
- **Failed queries**: Use the "Retry" button to generate a new SQL query for the same question

## Technical Architecture

- **Frontend**: Streamlit for the web interface
- **Data Processing**: Pandas for data manipulation
- **SQL Execution**: pandasql for running SQL on DataFrames
- **AI Integration**: OpenAI GPT-4o-mini for natural language to SQL conversion
- **Data Storage**: In-memory (no database required)

## Sample Data

The demo includes sample financial data with the following columns:
- Authorization Group
- Business Transaction Type
- Transaction Value
- Currency
- Debit/Credit Indicator
- Fiscal Year
- And more...

## Security Note

This demo includes a hardcoded OpenAI API key for demonstration purposes. In production, always use environment variables for API keys.

## Future Enhancements

- Support for multiple data sources
- Data visualization capabilities
- Export functionality
- User authentication
- Query history and favorites
- Advanced data quality checks 