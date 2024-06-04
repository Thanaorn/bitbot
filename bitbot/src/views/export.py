import csv
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
import seaborn as sns
from fpdf import FPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PyPDF2 import PdfMerger
from cryptography.fernet import Fernet
from datetime import datetime
import threading
import os
import pika
from flask import Flask, json
app = Flask(__name__)

def decrypt_message(key,message):
    f = Fernet(key)
    dec_message=f.decrypt(message)
    return dec_message.decode()

def cast_type_back(df2,column):
    df2[column] = df2[column].astype(int)
    
def sql_to_csv(cid,name):
    database_path = r'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\instance\database.db'
    fonts = r"C:\Users\thana\Downloads\Kanit\Kanit-Regular.ttf"
    pdf_file_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}.pdf"
    folder_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv"
    csv_file_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}.csv'
    engine = create_engine(f'sqlite:///{database_path}')
    
    query = f"SELECT index_id,date,income,expense,exercise,work,sleep,feeling,daily,key FROM user_habit WHERE id='{cid}' "
    df = pd.read_sql_query(query, engine)
    
    df.to_csv(csv_file_path, index=False,encoding="utf-8")
    print(f'Data exported to {csv_file_path}')
    #convert to pdf file
    df2 = pd.read_csv(rf'{folder_path}\{name}.csv')
    for i in range(df['income'].count()):
        key = df['key'][i]

        income_encrypted = df['income'][i]
        expense_encrypted = df['expense'][i]
        daily_encrypted = df['daily'][i]

        income_decrypted = decrypt_message(key,income_encrypted)
        expense_decrypted = decrypt_message(key,expense_encrypted)
        daily_decrypted = decrypt_message(key,daily_encrypted)

        df2.loc[i,'income'] = income_decrypted
        df2.loc[i,'expense'] = expense_decrypted
        df2.loc[i,'daily'] = daily_decrypted
    
    column_to_delete = 'key'
    if column_to_delete in df2.columns:
        del df2[column_to_delete]
    
    df2.to_csv(csv_file_path, index=False,encoding="utf-8")
    cast_type_back(df2,'income')
    cast_type_back(df2,'expense')
    
    
    csv_to_pdf(csv_file_path,pdf_file_path,fonts)
    try:
        merger = PdfMerger()
        merger.append(pdf_file_path)
        merger.append(rf'{folder_path}\{name}pie.pdf')
        merger.append(rf'{folder_path}\{name}summary.pdf')
        
        current_date = datetime.now()
        formatted_date = str(current_date.strftime('%d-%m-%Y'))
        with open(rf'{folder_path}\{name}{formatted_date}.pdf', 'wb') as fout:
            merger.write(fout)
    except Exception as e:
                print(f"Error pdf merger: {e}")
    
def csv_to_pdf(csv_file_path,pdf_file_path,fonts,df2,name):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Kanit', '', fonts, uni=True)
    pdf.set_font("Kanit", size = 12) 
    pdf.set_auto_page_break(auto=True, margin=15)
    try:
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
        plt.close('all')
        plot_col(df2,name)
        income_expenses(df2,name)
    except Exception as e:
                print(f"Error pdf table: {e}")
    
def plot_col(df,name):
    folder_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}pie.pdf"
    rows = ['exercise', 'work', 'feeling', 'sleep']
    colors = ['lightgreen', 'palegoldenrod', 'lightcoral']
    try:
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
    except Exception as e:
                print(f"Error piechart graph: {e}")

def income_expenses(df,name):
    folder_path = rf"C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}summary.pdf"
    # Plot a histogram for income and expense data
    total_income = df['income'].sum()
    total_expense = df['expense'].sum()
    remaining = total_income-total_expense
    # Plotting the total income and total expense
    try:
        bars=plt.bar(['Income', 'Expense','Remaining'], [total_income, total_expense,remaining], color=['dodgerblue', 'lightcoral','gold'])
        # Adding labels and title
        plt.xlabel('Category')
        plt.ylabel('Total Amount')
        plt.title('Total Income vs Total Expense')

        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')
        
        plt.savefig(folder_path)
        plt.close('all')
    except Exception as e:
                print(f"Error income graph: {e}")
    
def callback(ch, method, properties, body):
    def process():
        try:
            print(f" [x] Received message")
            message = json.loads(body)
            name = message['name']
            cid = message['cid']
            print(f"Message content: {message}")
            print(f" [x] Received send file request")
            sql_to_csv(cid,name)
            # You can perform additional processing here, if needed
        except Exception as e:
                print(f"Error processing message: {e}")

    thread = threading.Thread(target=process)
    thread.start()

if __name__ == "__main__":
    print("this is export")
    print("Connecting to RabbitMQ...")  
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    print("Connected to RabbitMQ.")
    channel.queue_declare(queue='export_file')

    channel.basic_consume(queue='export_file', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()