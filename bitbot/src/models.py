from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String,FLOAT
from sqlalchemy.orm import Mapped,relationship

from . import db


class UserHabit(db.Model):
    index_id=Column(Integer,index=True, primary_key=True)
    id = Column(String,index=True,nullable=False)
    income=Column(Integer,index=True,nullable=False)
    expense=Column(Integer,index=True,nullable=False)
    exercise=Column(Integer,index=True,nullable=False)
    work=Column(Integer,index=True,nullable=False)
    feeling=Column(Integer,index=True,nullable=False)
    sleep=Column(Integer,index=True,nullable=False)
    daily=Column(String,index=True,nullable=False)
    date=Column(String,index=True,nullable=False)
    key=Column(String,index=True,nullable=False)
    
class UserDate(db.Model):
    id = Column(String,index=True,nullable=False,primary_key=True)
    date=Column(String,index=True,nullable=False)
