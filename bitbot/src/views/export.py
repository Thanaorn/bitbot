import csv
import pandas as pd
from sqlalchemy import create_engine
#from csv2pdf import convert
#from urllib.parse import unquote
from fpdf import FPDF
def sql_to_csv(cid,name):
    
    # Define the file path to your SQLite database
    database_path = r'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\instance\database.db'
    fonts = r"C:\Users\thana\Downloads\Kanit\Kanit-Regular.ttf"
    pdf_file_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}.pdf"
    # Create SQLAlchemy engine
    engine = create_engine(f'sqlite:///{database_path}')

    # Define the SQL query to fetch data from the database
    query = f"SELECT index_id,date,income,expense,exercise,work,sleep,feeling,daily FROM user_habit WHERE id='{cid}' "

    # Read data from the database into a pandas DataFrame
    df = pd.read_sql_query(query, engine)

    # Define the file path for saving the CSV file
    csv_file_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}.csv'

    # Export the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False,encoding="utf-8")
    print(f'Data exported to {csv_file_path}')

    #convert to pdf file
    csv_to_pdf(csv_file_path,pdf_file_path,fonts)
    #convert(csv_file_path, pdf_file_path,font=fonts, headerfont=fonts)
    
def csv_to_pdf(csv_file_path,pdf_file_path,fonts):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Kanit', '', fonts, uni=True)
    pdf.set_font("Kanit", size = 12) 
    with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        header = next(reader)

        # Define column widths
        row_height = 6
        num_columns = len(header)
        available_width = pdf.w - (num_columns - 1) * 5  # Adjusting for cell borders
        col_widths_except_last = available_width / num_columns

        # Allocate more space for the last column
        last_col_width = col_widths_except_last * 2.5  # Adjust this factor as needed
        col_widths = [col_widths_except_last for _ in range(num_columns - 1)]
        col_widths.append(last_col_width)

        # Add table header
        pdf.set_fill_color(200, 220, 255)  # Light blue fill color for header
        pdf.set_text_color(0, 0, 0)  # Black text color
        pdf.set_font("Kanit", size=10)
        for i, header_text in enumerate(header):
            pdf.cell(col_widths[i], row_height, header_text, border=1, ln=False, align='C', fill=True)
        pdf.ln()

        # Reset font for data rows
        pdf.set_font("Kanit", size=8)
        pdf.set_fill_color(255)  # Reset fill color to default

        # Add data rows
        for row in reader:
            max_line_count = max(len(cell.split('\n')) for cell in row)  # Maximum line count in any cell of this row
            row_height = max_line_count * 5  # Assuming each line has a height of 5

            for i, cell in enumerate(row):
                lines = cell.split('\n')
                x = pdf.get_x()
                y = pdf.get_y()
                pdf.set_xy(x, y)
                for line in lines:
                    pdf.cell(col_widths[i], 5, line, border=1, align='L')
                pdf.set_xy(x + col_widths[i], y)

            # Reset the row height for the next row
            pdf.ln(row_height)
            row_height = 6
            
    pdf.output(pdf_file_path)
    
# def csv_to_graph(csv_file_path):
#     df = pd.read_csv(csv_file_path)
#     work_data = df['work']

#     # Calculate the count of each unique value
#     work_counts = work_data.value_counts()


#     # Plot a pie chart for the "work" column with explode settings
#     work_counts.plot(kind='pie', autopct='%1.1f%%')
#     # Plot a pie chart for the "work" column
#     plt.title('Work Distribution')
#     plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
#     plt.show()