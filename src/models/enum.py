from sqlalchemy import Enum


class InsuranceInfoEnum(Enum):
    Osago = "osago"
    Mortgage = "mortgage"
    Selfinsurance = "selfinsurance"
    Other = "other"
