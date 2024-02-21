from datetime import datetime

from pydantic import BaseModel


class UserData(BaseModel):
    id: int
    time_create: datetime
    time_insure_end: datetime
    first_name: str
    middle_name: str
    last_name: str
    phone: str
    email: str

