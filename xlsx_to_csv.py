import pandas as pd

# Read the Excel file (first sheet by default)
df = pd.read_excel('data/Data Dump - Accrual Accounts.xlsx')

# Write to CSV (without the index column)
df.to_csv('data/Data Dump - Accrual Accounts.csv', index=False) 