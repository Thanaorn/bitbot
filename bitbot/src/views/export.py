import csv
import pandas as pd

conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=RON-SQLEXPRESS;"
    "Database=test_database;"
    "Trusted_Connection=yes;"
)
sql_querry = pd.read_sql_table("user_habit",conn)
df = pd.DataFrame(sql_querry)
df.to_csv("", index=False)