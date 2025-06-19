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

class CustomerUpdate(BaseModel):
    name: str | None = None
    phone_number: str | None = None
    email: str | None = None
    address: str | None = None

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

class BillUpdate(BaseModel):
    customer_id: int | None = None
    billing_date: date | None = None
    due_date: date | None = None
    amount: float | None = None
    status: str | None = None


