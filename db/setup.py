from sqlalchemy import create_engine, Column, Integer, String, Boolean, BigInteger, JSON, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from utils import constants


try:
   engine = create_engine(constants.DB_URL)
except Exception as error:
    print("Error while connecting to PostgreSQL:", error)


Session = sessionmaker(bind=engine)
session = Session()
query = session.query


# Create a base class for declarative models
Base = declarative_base()

def get_db():
    db = Session

    try: 
        yield db
    except:
        db.close_all()



