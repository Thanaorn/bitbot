import requests
import json
import schedule
import time

# Your LINE channel access token
LINE_ACCESS_TOKEN = "_"

# URL for sending messages via LINE Messaging API
url = "http://127.0.0.1:5000/pushone"

user_id = "_"

# Define the message payload as a Python dictionary
message_payload = {
    "to": user_id,
    "messages": [
        {
            "type": "text",
            "text": "วันนี้คุณบันทึก habit แล้วหรือยัง"
        }
    ]
}

# Convert the message payload to JSON string
json_payload = json.dumps(message_payload)

# Define headers
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + LINE_ACCESS_TOKEN
}

# Function to send message
def send_message():
    response = requests.post(url, data=json_payload, headers=headers)
    print("Message sent. Response Status Code:", response.status_code)

# Schedule job to run every 5 minutes
schedule.every(1).minutes.do(send_message)

# Infinite loop to run the scheduler
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping the scheduler.")