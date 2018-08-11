# flask_sqlalchemy/models.py
from sqlalchemy import Column, Integer, String, DateTime
from scheduler.db import Base
from flask_login.mixins import UserMixin


class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer)
    title = Column(String)
    url = Column(String)
    status = Column(String)
    owner = Column(String)
    project = Column(String)
    created_date = Column(DateTime)
    modified_date = Column(DateTime)
    assigned_date = Column(DateTime)
    closed_date = Column(DateTime)
    priority = Column(Integer)


# Define User data-model
class User(Base):
    __tablename__ = 'users'
    email = Column(String(255), nullable=False, unique=True, primary_key=True)
    name = Column(String)
    surname = Column(String)
    fullname = Column(String)
    avatar = Column(String)


