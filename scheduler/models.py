# flask_sqlalchemy/models.py
from sqlalchemy import *
from .db import Base


class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer)
    title = Column(String)
    url = Column(String)
    status = Column(String)
    owner = Column(String)
    project = Column(String)
