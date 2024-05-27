import pandas as pd
from sqlalchemy import create_engine
def sql_to_csv(cid,name):
    # Define the file path to your SQLite database
    database_path = r'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\instance\database.db'
    # Create SQLAlchemy engine
    engine = create_engine(f'sqlite:///{database_path}')

    # Define the SQL query to fetch data from the database
    query = f"SELECT * FROM user_habit WHERE id='{cid}' "

    # Read data from the database into a pandas DataFrame
    df = pd.read_sql_query(query, engine)

    # Define the file path for saving the CSV file
    csv_file_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}.csv'

    # Export the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)

    print(f'Data exported to {csv_file_path}')
