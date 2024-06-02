from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String
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
# class IdKey(db.Model):
#     __tablename__ = 'id_key'  # Define the table name explicitly
#     id = Column(String, primary_key=True,index=True)  # Designate 'id' as the primary key
#     user_id = Column(String, ForeignKey('user_habit.id'), index=True, nullable=True)
#     key = Column(String, index=True, nullable=True)
#     user_habit = relationship('UserHabit', backref='id_keys')
