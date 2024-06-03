from datetime import datetime
import requests
import schedule
import time
import pandas as pd
from sqlalchemy import create_engine

LINE_ACCESS_TOKEN = "IaOocLOEQx4VhqsIPRzR1yFtMI831tALheSTsCCl54wlnTIwCj1rELDnlCtZXuSPxxBLKUS5VQHV2VtXkq5ewSCq4Z2sxT4scfq6eCmZW4kExTcyh9JsPGm8TLGDSzplZSyiqPuaMRwPNDw1DHVjbAdB04t89/1O/w1cDnyilFU="
user_id = "U4f937a2f31fb4d02e9f552c4d40f5fa2"
#user_id = "U16cbbdc57e4f3a0df2099d022d693f80"
LINE_API_URL = "https://api.line.me/v2/bot/message/push"
#LINE_API_URL = "https://api.line.me/v2/bot/message/broadcast"
# push only one person

headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
    }
payload = {
        "to": user_id,
        "messages": [
            {
                "type":"text",
                "text":"วันนี้ได้ทำHabit trackerยัง?"
            }
        ]
    }

# boardcast
# headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
#     }
# payload = {
#         "messages": [
#             {
#                 "type":"text",
#                 "text":"วันนี้ได้ทำHabit trackerยัง?"
#             }
#         ]
#     }

# def send_message():
#     response = requests.post(LINE_API_URL,headers=headers, json=payload)
#     print("Message sent. Response Status Code:", response.status_code)

def send_message():#multicast send all who didn't use today
    LINE_API_URL = "https://api.line.me/v2/bot/message/multicast"
    database_path = r'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\instance\database.db'
    engine = create_engine(f'sqlite:///{database_path}')
        
    current_date = datetime.now()
    formatted_date = current_date.strftime('%d/%m/%Y')
    print(type(formatted_date))
    query = f"SELECT DISTINCT id FROM user_date WHERE date!='{formatted_date}'"
    df = pd.read_sql_query(query, engine)
    list_of_dicts = df.to_dict('list')
    print("list=",list_of_dicts)
    print(list_of_dicts['id'])
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
    }
    payload = {
            "to": list_of_dicts['id'],
            "messages": [
                {
                    "type":"text",
                    "text":"วันนี้จะไม่ทำ habbit tracker หรอ?"
                }
            ]
        }
    
    response = requests.post(LINE_API_URL,headers=headers, json=payload)
    print("Message sent. Response Status Code:", response.status_code)
    

# Schedule job to run every 5 seconds
#schedule.every(5).seconds.do(send_message)

scheduled_time = "22:30"
schedule.every().day.at(scheduled_time).do(send_message)
try:
    while True:
        schedule.run_pending()
        print(datetime.now())
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping the scheduler.")