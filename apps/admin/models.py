from sqlalchemy import Column, Integer, String, BigInteger, JSON
from db.setup import session, Base


# Define the 'Admin' table
# 
class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    userId = Column(BigInteger)

    def __init__(self, userId):
        self.userId = userId


    @classmethod
    def isAdmin(self, userId):
        
        try:
            admin = session.query(Admin).filter_by(userId=userId).first()
            session.commit()

        except Exception as e:
            # If an exception occurs, rollback the transaction
            session.rollback()
            raise e
        finally:
            # Always close the session
            session.close()

        
        return admin is not None

    def register(self, user_id):
        if not self.__class__.isAdmin(user_id):
            self.user_id = user_id
            self.save()

    def save(self):
        session.add(self)
        session.commit()


