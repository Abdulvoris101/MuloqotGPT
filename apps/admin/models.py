from sqlalchemy import Column, Integer, BigInteger
from db.setup import session, Base


class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    userId = Column(BigInteger)

    def __init__(self, userId):
        self.userId = userId

    @classmethod
    def isAdmin(cls, userId):
        try:
            admin = session.query(Admin).filter_by(userId=userId).first()
            session.commit()
        except Exception as e:
            raise e
        finally:
            session.close()

        return admin is not None

    def register(self):
        if not self.__class__.isAdmin(self.userId):
            self.save()

    def save(self):
        session.add(self)
        session.commit()


