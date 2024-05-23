import hashlib
from flask import Blueprint, json, jsonify,request
from ..models import db,UserHabit
from sqlalchemy import select, update
import os
import redis
bp = Blueprint("index", __name__, url_prefix="/")

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = os.getenv('REDIS_PORT', 6379)
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
expiration_time = 60

def adjust_data(data):
    json_string = data.decode('utf-8')
    json_data = json.loads(json_string)
    work_value = json_data["work"]
    number_only = work_value.split(":")[1]
    json_data= int(number_only)
    return json_data


@bp.route("", methods=["GET"])
def get_test():
    return "SUCCESS",200

@bp.route("/postsleep", methods=["POST"])
def post_sleep():
    if request.data:
        data = request.data
        json_data={"sleep":adjust_data(data)}
        print(json_data)
        return "success", 201
    else:
        return "failed to recive data",400
    
@bp.route("/postwork", methods=["POST"])
def post_work():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        uid = data2["userID"]
        json_data={"work":adjust_data(data)}
        print(data)
        print(uid)
        print(json_data)
        ub = UserHabit()
        
        ub.id=uid
        ub.work=adjust_data(data)
        """"
        ub.expense=9000
        ub.income=10000
        ub.sleep=1
        ub.feeling=2
        ub.exercise=3
        db.session.add(ub)
        db.session.commit()
        """
        return {"status":"insert success"}, 201
    else:
        return "failed to recive data",400

@bp.route("/postallscore", methods=["POST"])
def post_all():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        uid = data2["cid"]
        uid_encode = hashlib.sha256(uid.encode()).hexdigest()
        print(data)
        print("userID : ",uid_encode)
        print("exercise : ",data2["exercise"])
        print("sleep : ",data2["sleep"])
        print("work : ",data2["work"])
        print("feeling : ",data2["feeling"])
        print("income : ",data2["income"])
        print("expense : ",data2["expense"])
        
        r.set(uid_encode+"id",uid_encode)
        r.set(uid_encode+"exercise",data2["exercise"])
        r.set(uid_encode+"sleep",data2["sleep"])
        r.set(uid_encode+"work",data2["work"])
        r.set(uid_encode+"feeling",data2["feeling"])
        r.set(uid_encode+"income",data2["income"])
        r.set(uid_encode+"expense",data2["expense"])
        return {"status":"set to redis"}, 201
    else:
        return "failed to recive data",400
    
@bp.route("/confirmdata", methods=["POST"])
def confirm_data():
    if request.data:
        data = request.data
        data2 = json.loads(data)
        uid = data2["cid"]
        uid_encode = hashlib.sha256(uid.encode()).hexdigest()
        if data2["status"] == "ถูกต้อง":
            print(data2)
            ub = UserHabit()
            ub.id = r.get(uid_encode+"id")
            ub.exercise = r.get(uid_encode+"exercise")
            ub.sleep = r.get(uid_encode+"sleep")
            ub.work = r.get(uid_encode+"work")
            ub.feeling = r.get(uid_encode+"feeling")
            ub.income = r.get(uid_encode+"income")
            ub.expense = r.get(uid_encode+"expense")
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
            return {"status":"cancel data"},400