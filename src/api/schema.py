import re
from datetime import datetime, date

from pydantic import BaseModel, EmailStr, validator, Field

from src.models.enum import InsuranceInfoEnum


class InsuranceInfoSchema(BaseModel):
    description: str
    polis_type: str = InsuranceInfoEnum
    polis_extended: bool = Field(default=False)
    time_insure_end: date

    class Config:
        use_enum_values = True


class UserDataSchema(InsuranceInfoSchema):
    time_create: datetime
    first_name: str
    middle_name: str
    last_name: str
    phone: str
    email: EmailStr

    @validator('phone')
    def phone_validator(cls, v):
        phone_number = re.sub(r"\D", "", v)

        if phone_number.startswith(('8', '7', '+7')):
            phone_number = phone_number.lstrip('8').lstrip('7').lstrip('+')

        if len(phone_number) != 10:
            raise ValueError('Номер телефона должен содержать 10 цифр после удаления кода страны')

        return phone_number
