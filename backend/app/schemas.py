from pydantic import BaseModel
from datetime import date

class CustomerBase(BaseModel):
    name: str
    phone_number: str
    email: str
    address: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    customer_id: int
    class Config:
        orm_mode = True

class BillBase(BaseModel):
    customer_id: int
    billing_date: date
    due_date: date
    amount: float
    status: str

class BillCreate(BillBase):
    pass

class Bill(BillBase):
    bill_id: int
    class Config:
        orm_mode = True

