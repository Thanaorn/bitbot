from datetime import datetime
import requests
import json
import schedule
import time
import subprocess

url = "http://127.0.0.1:5000/pushone"


def send_message():
    response = requests.post(url)
    print("Message sent. Response Status Code:", response.status_code)
    
    
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