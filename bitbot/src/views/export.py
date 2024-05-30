import csv
import threading
import pandas as pd
from sqlalchemy import create_engine
#from csv2pdf import convert
#from urllib.parse import unquote
import numpy as np
import seaborn as sns
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PyPDF2 import PdfMerger

def sql_to_csv(cid,name):
    database_path = r'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\instance\database.db'
    fonts = r"C:\Users\thana\Downloads\Kanit\Kanit-Regular.ttf"
    pdf_file_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}.pdf"
    folder_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv"

    engine = create_engine(f'sqlite:///{database_path}')
    
    query = f"SELECT index_id,date,income,expense,exercise,work,sleep,feeling,daily FROM user_habit WHERE id='{cid}' "
    df = pd.read_sql_query(query, engine)
    csv_file_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}.csv'
    df.to_csv(csv_file_path, index=False,encoding="utf-8")
    print(f'Data exported to {csv_file_path}')
    #convert to pdf file
    csv_to_pdf(csv_file_path,pdf_file_path,fonts)
    #df2 = pd.read_csv(rf'{folder_path}\{name}.csv')
    plot_col(df,name)
    income_expenses(df,name)
    merger = PdfMerger()
    merger.append(pdf_file_path)
    merger.append(rf'{folder_path}\{name}pie.pdf')
    merger.append(rf'{folder_path}\{name}summary.pdf')

    with open(rf'{folder_path}\{name}final.pdf', 'wb') as fout:
        merger.write(fout)
    
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
    
def plot_col(df,name):
    folder_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}pie.pdf"
    rows = ['exercise', 'work', 'feeling', 'sleep']
    colors = ['lightgreen', 'palegoldenrod', 'lightcoral']

    fig, axs = plt.subplots(2, 2, figsize=(7, 7))  # Set the size of the figure and create subplots

    for i, row in enumerate(rows):
        data = df[row]
        counts = data.value_counts()
        r = i // 2  # Row index
        c = i % 2   # Column index
        axs[r, c].pie(counts, labels=counts.index, autopct='%1.1f%%', colors=colors, startangle=140)
        axs[r, c].set_title(f'{row.capitalize()} Ratio')
        axs[r, c].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.tight_layout()
    plt.savefig(folder_path)
    plt.close('all')

def income_expenses(df,name):
    folder_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}summary.pdf"
    # Plot a histogram for income and expense data
    total_income = df['income'].sum()
    total_expense = df['expense'].sum()
    remaining = total_income-total_expense
    # Plotting the total income and total expense
    plt.bar(['Income', 'Expense','Remaining'], [total_income, total_expense,remaining], color=['dodgerblue', 'lightcoral','gold'])
    # Adding labels and title
    plt.xlabel('Category')
    plt.ylabel('Total Amount')
    plt.title('Total Income vs Total Expense')
    
    for i, v in enumerate([total_income, total_expense, remaining]):
        plt.text(i, v + 50, str(v), ha='center')
        
    plt.savefig(folder_path)
    plt.close('all')