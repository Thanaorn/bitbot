from datetime import datetime
import hashlib
from flask import Blueprint, json, jsonify, render_template,request, send_file
import requests
from ..models import db,UserHabit
from sqlalchemy import select, update
import os
import redis
from ..views import export
import threading
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
bp = Blueprint("index", __name__, url_prefix="/")

#redis create 
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
expiration_time = 60

def encode_id(cid):
    return hashlib.sha256(cid.encode()).hexdigest()

def is_file_in_folder(folder_path, filename):
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        print(f"The file '{filename}' exists in the folder.")
        return True
    else:
        print(f"The file '{filename}' does not exist in the folder.")
        return False
    
def sql_to_update_table(index_value,uid_encode):
    try:
        ub = UserHabit()
        # Update the table    
        values = {
                "income": r.getdel(uid_encode+"income_edit"),
                "expense": r.getdel(uid_encode+"expense_edit"),
                "sleep": r.getdel(uid_encode+"sleep_edit"),
                "feeling": r.getdel(uid_encode+"feeling_edit"),
                "work":r.getdel(uid_encode+"work_edit"),
                "exercise":r.getdel(uid_encode+"exercise_edit"),
                "daily":r.getdel(uid_encode+"daily_edit")
            }
        db.session.execute(update(UserHabit).where(UserHabit.index_id==index_value).values(values))
        db.session.commit()

        print(f'Table updated with data for index {index_value}')
        
    except Exception as e:
        db.session.rollback()
        print(f'Error updating table: {e}')
    

@bp.route("/", methods=["GET"])
def get_test():
    return render_template('index.html.jinja'),200

@bp.route("/getpayload", methods=["GET"])
def get_payload():
    data = {
        "data":"test123"
    }
    return jsonify(data)

@bp.route("/webpage",methods=["GET"])
def get_webpage():
    pdf_path=r'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\ThanatornTyfinal.pdf'
    return render_template('pdf.html', pdf_url=pdf_path),200
    
@bp.route("/link", methods=["GET"])
def link_download():
    data = request.args
    name = data["name"]
    print(name)
    folder_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv'
    if is_file_in_folder(folder_path, f"{name}final.pdf"):
        csv_file_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}final.pdf'
        return send_file(csv_file_path, as_attachment=True)
    else:
        return 'file doesn\'t exit '
    
@bp.route("/download", methods=["POST"])
def download():
    name = request.form['name']
    print("Name:",name)
    folder_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv'
    if is_file_in_folder(folder_path, f"{name}.pdf"):
        file_path = rf'C:\Users\thana\Desktop\Py\bitbitbotbot2\bitbot\bitbot\src\views\keepcsv\{name}.pdf'
        return send_file(file_path, as_attachment=True)
    else:
        return render_template('index.html.jinja'),401

@bp.route("/postallscore", methods=["POST"])
def post_all():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        uid = data2["cid"]
        uid_encode = encode_id(uid)
        print(data)
        print("userID : ",uid_encode)
        print("exercise : ",data2["exercise"])
        print("sleep : ",data2["sleep"])
        print("work : ",data2["work"])
        print("feeling : ",data2["feeling"])
        print("income : ",data2["income"])
        print("expense : ",data2["expense"])
        print("daily : ",data2["daily"])
        r.set(uid_encode+"id",uid_encode)
        r.set(uid_encode+"exercise",data2["exercise"])
        r.set(uid_encode+"sleep",data2["sleep"])
        r.set(uid_encode+"work",data2["work"])
        r.set(uid_encode+"feeling",data2["feeling"])
        r.set(uid_encode+"income",data2["income"])
        r.set(uid_encode+"expense",data2["expense"])
        r.set(uid_encode+"daily",data2["daily"])
        return {"status":"set to redis"}, 201
    else:
        return "failed to recive data",400

@bp.route("/confirmdata", methods=["POST"])
def confirm_data():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        uid = data2["cid"]
        uid_encode = encode_id(uid)
        if data2["status"] == "ถูกต้อง":
            print(data2)
            ub = UserHabit()
            ub.id = r.getdel(uid_encode+"id")
            ub.exercise = r.getdel(uid_encode+"exercise")
            ub.sleep = r.getdel(uid_encode+"sleep")
            ub.work = r.getdel(uid_encode+"work")
            ub.feeling = r.getdel(uid_encode+"feeling")
            ub.income = r.getdel(uid_encode+"income")
            ub.expense = r.getdel(uid_encode+"expense")
            ub.daily = r.getdel(uid_encode+"daily")
            current_date = datetime.now()
            formatted_date = current_date.strftime('%d/%m/%Y')
            ub.date = formatted_date
            db.session.add(ub)
            db.session.commit()
            return {"status":"add to database"},200
        else:
            r.delete(uid_encode+"id")
            r.delete(uid_encode+"exercise")
            r.delete(uid_encode+"sleep")
            r.delete(uid_encode+"work")
            r.delete(uid_encode+"feeling")
            r.delete(uid_encode+"income")
            r.delete(uid_encode+"expense")
            r.delete(uid_encode+"daily")
            return {"status":"cancel data"},400
    
@bp.route("/editdata", methods=["POST"])
def edit_data():
    data = request.data
    data2 = json.loads(data)
    uid = data2["cid"]
    index=data2["index"]
    uid_encode = encode_id(uid)
    print(uid_encode)
    print(index)
    user = UserHabit.query.filter_by(index_id=index,id=uid_encode).first()
    if not user:
        print("wrong index")
        return {"status":"invalid id"},400
    else:
        r.set(uid_encode+"index_id_edit",index)
        r.set(uid_encode+"id_edit",uid_encode)
        r.set(uid_encode+"exercise_edit",data2["exercise"])
        r.set(uid_encode+"sleep_edit",data2["sleep"])
        r.set(uid_encode+"work_edit",data2["work"])
        r.set(uid_encode+"feeling_edit",data2["feeling"])
        r.set(uid_encode+"income_edit",data2["income"])
        r.set(uid_encode+"expense_edit",data2["expense"])
        r.set(uid_encode+"daily_edit",data2["daily"])
        return "แก้ไขเสร็จสิ้น"
    
@bp.route("/confirmedit", methods=["POST"])
def confirm_edit():
    data = request.data
    data2 = json.loads(data)
    uid = data2["cid"]
    uid_encode = encode_id(uid)
    index= r.getdel(uid_encode+"index_id_edit")
    print(uid_encode)
    print(index)
    if data2["status"] == "ถูกต้อง":
        sql_to_update_table(index,uid_encode)
        return {"status":"confirm edit"},200
    else:
        r.delete(uid_encode+"id_edit")
        r.delete(uid_encode+"exercise_edit")
        r.delete(uid_encode+"sleep_edit")
        r.delete(uid_encode+"work_edit")
        r.delete(uid_encode+"feeling_edit")
        r.delete(uid_encode+"income_edit")
        r.delete(uid_encode+"expense_edit")
        r.delete(uid_encode+"daily_edit")
        return {"status":"cancel edit"}
    
@bp.route("/exportdata", methods=["POST"])
def export_data():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        cid = data2["cid"]
        name = data2["name"]
        cid_encode = encode_id(cid)
        print(cid_encode)
        print(name)
        #export.sql_to_csv(cid_encode,name)
        t = threading.Thread(target=export.sql_to_csv, args=(cid_encode,name,))
        t.setDaemon(True)
        t.start()
    return {"status":"success"}

@bp.route("/pushone", methods=["POST"])
def push_one():
    LINE_ACCESS_TOKEN = "IaOocLOEQx4VhqsIPRzR1yFtMI831tALheSTsCCl54wlnTIwCj1rELDnlCtZXuSPxxBLKUS5VQHV2VtXkq5ewSCq4Z2sxT4scfq6eCmZW4kExTcyh9JsPGm8TLGDSzplZSyiqPuaMRwPNDw1DHVjbAdB04t89/1O/w1cDnyilFU="
    user_id = "U4f937a2f31fb4d02e9f552c4d40f5fa2"
    LINE_API_URL = "https://api.line.me/v2/bot/message/push"
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
    response = requests.post(LINE_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return jsonify({"status": "success", "message": "Message sent successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to send message"}), response.status_code
