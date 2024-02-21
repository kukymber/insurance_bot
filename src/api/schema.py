from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
import re

class UserDataSchema(BaseModel):
    time_insure_end: datetime
    first_name: str
    middle_name: str
    last_name: str
    phone: str
    email: EmailStr

    @validator('phone')
    def phone_validator(cls, v):
        phone_number = re.sub(r"\D", "", v)

        if not phone_number.startswith(('8', '7')):
            raise ValueError('Номер телефона должен начинаться с +7 или 8')

        if len(phone_number) != 11:
            raise ValueError('Номер телефона должен содержать 11 цифр')

        if phone_number.startswith('8'):
            phone_number = '+7' + phone_number[1:]

        return phone_number



