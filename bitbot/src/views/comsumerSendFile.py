import threading
import os
from flask import json, send_file
import pika

print("Connecting to RabbitMQ...")  
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
print("Connected to RabbitMQ.")
channel.queue_declare(queue='send_file_to_user')

def send_path_to_user(pdf_file_path):
    return pdf_file_path

def callback(ch, method, properties, body):
    def process():
        try:
            print(f" [x] Received message")
            message = json.loads(body)
            pdf_file_path = message['path']
            print(f"Message content: {message}")
            print("pdf path:", pdf_file_path)
            print(f" [x] Received send file request")
            # You can perform additional processing here, if needed
            send_path_to_user(pdf_file_path)
        except Exception as e:
                print(f"Error processing message: {e}")

    thread = threading.Thread(target=process)
    thread.start()

channel.basic_consume(queue='send_file_to_user', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

