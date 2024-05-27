from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String


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



