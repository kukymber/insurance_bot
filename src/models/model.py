from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserData(Base):
    __tablename__ = "user_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_create = Column(DateTime(timezone=True), nullable=True)
    time_insure_end = Column(Date, nullable=True)
    first_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'time_create': self.time_create.isoformat() if self.time_create else None,
            'time_insure_end': self.time_insure_end.isoformat() if self.time_insure_end else None,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email
        }
