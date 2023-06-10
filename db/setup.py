from sqlalchemy import create_engine, Column, Integer, String, Boolean, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Create the engine and session

try:
   engine = create_engine('postgresql://postgres:postgres@localhost:5432/muloqotai')
except Exception as error:
    print("Error while connecting to PostgreSQL:", error)


Session = sessionmaker(bind=engine)
session = Session()


# Create a base class for declarative models
Base = declarative_base()



# Create all the tables
Base.metadata.create_all(engine)

# Commit the changes and close the session
session.commit()
