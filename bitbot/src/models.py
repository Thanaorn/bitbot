from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String,FLOAT
from sqlalchemy.orm import Mapped,relationship

from . import db


class UserHabit(db.Model):
    index_id=Column(Integer,index=True, primary_key=True)
    id = Column(String,index=True,nullable=True)
    income=Column(Integer,index=True,nullable=True)
    expense=Column(Integer,index=True,nullable=True)
    exercise=Column(Integer,index=True,nullable=True)
    work=Column(Integer,index=True,nullable=True)
    feeling=Column(Integer,index=True,nullable=True)
    sleep=Column(Integer,index=True,nullable=True)
    daily=Column(String,index=True,nullable=True)
    date=Column(String,index=True,nullable=True)
    key=Column(String,index=True,nullable=True)
class UserDate(db.Model):
    id = Column(String,index=True,nullable=True,primary_key=True)
    date=Column(String,index=True,nullable=True)
