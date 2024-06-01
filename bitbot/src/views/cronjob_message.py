from datetime import datetime
import requests
import schedule
import time

LINE_ACCESS_TOKEN = "IaOocLOEQx4VhqsIPRzR1yFtMI831tALheSTsCCl54wlnTIwCj1rELDnlCtZXuSPxxBLKUS5VQHV2VtXkq5ewSCq4Z2sxT4scfq6eCmZW4kExTcyh9JsPGm8TLGDSzplZSyiqPuaMRwPNDw1DHVjbAdB04t89/1O/w1cDnyilFU="
user_id = "U4f937a2f31fb4d02e9f552c4d40f5fa2"
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
                "text":"Hello, world id "
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
#                 "text":"Hello, world id "
#             }
#         ]
#     }
def send_message():
    response = requests.post(LINE_API_URL,headers=headers, json=payload)
    print("Message sent. Response Status Code:", response.status_code)
def check_using():
    return
    
# Schedule job to run every 5 minutes
schedule.every(5).seconds.do(send_message)
# Infinite loop to run the scheduler

try:
    while True:
        schedule.run_pending()
        print(datetime.now())
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping the scheduler.")