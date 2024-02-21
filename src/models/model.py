from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserData(Base):
    __tablename__ = "user_data"

    id: Mapped[int] = mapped_column(
        int, doc="Идентификатор", primary_key=True, autoincrement=True
    )
    time_create: Mapped[datetime] = mapped_column(
        DateTime(), doc="Дата списания", nullable=True
    )
    time_insure_end: Mapped[datetime] = mapped_column(
        DateTime(), doc="Дата окончания полиса", nullable=True)
    first_name: Mapped[str] = mapped_column(
        String(), doc="Имя", nullable=True)
    middle_name: Mapped[str] = mapped_column(
        String(), doc="Отчество", nullable=True)
    last_name: Mapped[str] = mapped_column(
        String(), doc="Фамилия", nullable=True)
    phone: Mapped[str] = mapped_column(
        String(), doc="Телефон", nullable=True)
    email: Mapped[str] = mapped_column(
        String(), doc="Email", nullable=True)

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
