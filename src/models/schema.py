from datetime import datetime, date

from pydantic import BaseModel
from sqlalchemy import Enum

from src.models.enum import InsuranceInfoEnum


class UserDataSchema(BaseModel):
    id: int
    time_create: datetime
    time_insure_end: date
    first_name: str
    middle_name: str
    last_name: str
    phone: str
    email: str


class InsuranceInfoSchema(BaseModel):
    id: int
    description: str
    polis_type: Enum[InsuranceInfoEnum]
    polis_extended: bool
    user_id: int
