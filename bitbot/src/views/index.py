from datetime import datetime, timedelta
from flask import Blueprint, Flask, json, jsonify, render_template,request, send_file
import pika
import requests
from ..models import db,UserHabit,UserDate
from sqlalchemy import select, update
import os
import redis
from ..views import export
import threading
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from cryptography.fernet import Fernet
import hashlib
from celery import Celery

bp = Blueprint("index", __name__, url_prefix="/")
#redis create 
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
@app.task
def process_data(uid, data):
    r.rpush(uid+"id", uid)
    r.rpush(uid+"exercise", data["exercise"])
    r.rpush(uid+"sleep", data["sleep"])
    r.rpush(uid+"work", data["work"])
    r.rpush(uid+"feeling", data["feeling"])
    r.rpush(uid+"income", data["income"])
    r.rpush(uid+"expense", data["expense"])
    r.rpush(uid+"daily", data["daily"])
    
@app.task    
def use_data(uid):
    key=genKey()
    fernet=token(key)
    ub = UserHabit()
    ub.id = r.rpop(uid+"id")
    ub.exercise = r.rpop(uid+"exercise")
    ub.sleep = r.rpop(uid+"sleep")
    ub.work = r.rpop(uid+"work")
    ub.feeling = r.rpop(uid+"feeling")
    ub.income = encrypt_message(fernet,r.rpop(uid+"income")).decode()
    ub.expense = encrypt_message(fernet,r.rpop(uid+"expense")).decode()
    ub.daily = encrypt_message(fernet,r.rpop(uid+"daily")).decode()
    ub.key = key.decode()
    #yesterday
    # today = datetime.now()
    # yesterday = today - timedelta(days=1)
    # formatted_date = yesterday.strftime("%d/%m/%Y")
    
    current_date = datetime.now()
    formatted_date = current_date.strftime('%d/%m/%Y')
    ub.date = formatted_date
    db.session.add(ub)
    db.session.commit()
    ######
    user = UserDate.query.filter_by(id=uid).first()
    if user:
        values = {"date":formatted_date}
        db.session.execute(update(UserDate).where(UserDate.id==uid).values(values))
        db.session.commit() 
    else:
        ud = UserDate()
        ud.id=uid
        ud.date=formatted_date
        db.session.add(ud)
        db.session.commit()
@app.task
def del_data(uid):
    r.delete(uid+"id")
    r.delete(uid+"exercise")
    r.delete(uid+"sleep")
    r.delete(uid+"work")
    r.delete(uid+"feeling")
    r.delete(uid+"income")
    r.delete(uid+"expense")
    r.delete(uid+"daily")
    
@app.task    
def sql_to_update_table(index_value,uid):
    try:
        key=genKey()
        fernet=token(key)
        values = {
                "income": encrypt_message(fernet,r.getdel(uid+"income_edit")).decode(),
                "expense": encrypt_message(fernet,r.getdel(uid+"expense_edit")).decode(),
                "sleep": r.getdel(uid+"sleep_edit"),
                "feeling": r.getdel(uid+"feeling_edit"),
                "work":r.getdel(uid+"work_edit"),
                "exercise":r.getdel(uid+"exercise_edit"),
                "daily":encrypt_message(fernet,r.getdel(uid+"daily_edit")).decode(),
                "key":key
            }
        db.session.execute(update(UserHabit).where(UserHabit.index_id==index_value).values(values))
        db.session.commit() 

        print(f'Table updated with data for index {index_value}')
        
    except Exception as e:
        db.session.rollback()
        print(f'Error updating table: {e}')
@app.task
def set_edit_data(index,uid,data2):
    r.set(uid+"index_id_edit",index)
    r.set(uid+"id_edit",uid)
    r.set(uid+"exercise_edit",data2["exercise"])
    r.set(uid+"sleep_edit",data2["sleep"])
    r.set(uid+"work_edit",data2["work"])
    r.set(uid+"feeling_edit",data2["feeling"])
    r.set(uid+"income_edit",data2["income"])
    r.set(uid+"expense_edit",data2["expense"])
    r.set(uid+"daily_edit",data2["daily"])
@app.task
def del_edit_data(uid):
    r.delete(uid+"id_edit")
    r.delete(uid+"exercise_edit")
    r.delete(uid+"sleep_edit")
    r.delete(uid+"work_edit")
    r.delete(uid+"feeling_edit")
    r.delete(uid+"income_edit")
    r.delete(uid+"expense_edit")
    r.delete(uid+"daily_edit")

def token(key):
    f = Fernet(key)
    return f
def genKey():
    key = Fernet.generate_key()
    return key
def encrypt_message(key,message):
    en_message = key.encrypt(message.encode())
    return en_message

def is_file_in_folder(folder_path, filename):
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        print(f"The file '{filename}' exists in the folder.")
        return True
    else:
        print(f"The file '{filename}' does not exist in the folder.")
        return False
    
@bp.route("/", methods=["GET"])
def get_test():
    return render_template('index.html.jinja'),200

@bp.route("/link", methods=["GET"])
def link_download():
    data = request.args
    name = data["name"]
    print(name)
    folder_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv'
    current_date = datetime.now()
    formatted_date = str(current_date.strftime('%d-%m-%Y'))
    if is_file_in_folder(folder_path, f"{name}{formatted_date}.pdf"):
        pdf_file_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}{formatted_date}.pdf'
        return send_file(pdf_file_path,as_attachment=True)
    else:
        return 'file doesn\'t exit '
    
@bp.route("/testpostallqueue", methods=["POST"])
def set_queue():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        uid = data2["cid"]
        if data2["daily"]=="ไม่" or data2["daily"]=="no":
            data2["daily"]=""
        process_data(uid, data2) 
        return {"status": "Data enqueued for processing"}, 201
    else:
        return "Failed to receive data", 400
    
@bp.route("/confirmallqueue", methods=["POST"])
def get_queue():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        uid = data2["cid"]
        if data2["status"] == "ถูกต้อง":
            use_data(uid) 
            return {"status": "Data dequeued for processing"}, 201
        else:
            del_data(uid) 
            return {"status":"cancel data"},400
    else:
        return "Failed to receive data", 400
#----------------------------------------------------------------------#

    
@bp.route("/editdata", methods=["POST"])
def edit_data():
    data = request.data
    data2 = json.loads(data)
    uid = data2["cid"]
    index=data2["index"]
    print(uid)
    print(index)
    user = UserHabit.query.filter_by(index_id=index,id=uid).first()
    if not user:
        print("wrong index")
        return {"status":"invalid id"},400
    else:
        if data2["daily"]=="ไม่" or data2["daily"]=="no":
            data2["daily"]=""
        set_edit_data(index,uid,data2)
        return "แก้ไขเสร็จสิ้น"
    
@bp.route("/confirmedit", methods=["POST"])
def confirm_edit():
    data = request.data
    data2 = json.loads(data)
    uid = data2["cid"]
    index= r.getdel(uid+"index_id_edit")
    print(uid)
    print(index)
    if data2["status"] == "ถูกต้อง":
        sql_to_update_table(index,uid)
        return {"status":"confirm edit"},200
    else:
        del_edit_data(uid)
        return {"status":"cancel edit"}
    
@bp.route("/exportdata", methods=["POST"])
def export_data():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        cid = data2["cid"]
        name = data2["name"]
        print(cid)
        print(name)
        #export.sql_to_csv(cid_encode,name)
        try:
            print(f"Connecting to RabbitMQ")
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            channel = connection.channel()

            channel.queue_declare(queue='export_file')

            message = json.dumps({'name':name,'cid':cid})

            channel.basic_publish(exchange='', routing_key='export_file', body=message)
            print(f" [x] Sent export request")
            connection.close()
        except Exception as e:
            print(f"Error export request: {e}") 
    return {"status":"success"}

