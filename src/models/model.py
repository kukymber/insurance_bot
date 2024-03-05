from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.models.enum import InsuranceInfoEnum

Base = declarative_base()


# TODO написать функцию для автоматического создания to_dict()

class UserData(Base):
    __tablename__ = "user_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time_create = Column(DateTime(timezone=True), nullable=True)
    first_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    insurance = relationship("InsuranceInfo", back_populates="user")

    def to_dict(self):
        return {
            'id': self.id,
            'time_create': self.time_create.isoformat() if self.time_create else None,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email
        }


class InsuranceInfo(Base):
    __tablename__ = "insurance_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=True)
    time_insure_end = Column(Date, nullable=True)
    polis_type = Column(Enum(InsuranceInfoEnum, name="insurance_info_enum"), nullable=False)
    polis_extended = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('user_data.id', onupdate="RESTRICT", ondelete="RESTRICT"))

    user = relationship("UserData", back_populates="insurance")

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'time_insure_end': self.time_insure_end.isoformat() if self.time_insure_end else None,
            'polis_type': self.polis_type.value if self.polis_type else None,
            'polis_extended': self.polis_extended,
            'user_id': self.user_id,
        }
