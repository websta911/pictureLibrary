from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base


basedir = os.path.abspath(os.path.dirname(__file__))

engine = create_engine('sqlite:///' +os.path.join(basedir, 'picLib.db'), echo=True)
Base = declarative_base()



class Subscription(Base):
    
    __tablename__ = "subscription"

    id = Column(Integer, primary_key = True)
    imagesrc = Column(String)
    email =  Column(String)
    va = Column(String)
    
    def __init__(self, imagesrc, email, va):
        self.imagesrc = imagesrc
        self.email = email
        self.va = va

class User(Base):
    """"""
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
 
    #----------------------------------------------------------------------
    def __init__(self, username, password):
        """"""
        self.username = username
        self.password = password

class Event(Base):
    
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event = Column(String)
    eDate = Column(String)
    eDesc = Column(String)
    eBg = Column(String)
    eLogo = Column(String)
    eShort = Column(String)
    eactive = Column(Integer)

    def __init__(self, event, eDate, eDesc, eBg, eLogo, eShort,eactive):
        self.event = event
        self.eDate = eDate
        self.eDesc = eDesc
        self.eBg = eBg
        self.eLogo = eLogo
        self.eShort = eShort
        self.eactive = eactive



Base.metadata.create_all(engine)