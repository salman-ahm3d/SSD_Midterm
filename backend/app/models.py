from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone_number = Column(String, unique=True)
    email = Column(String)
    address = Column(String)

class Bill(Base):
    __tablename__ = "bills"

    bill_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    billing_date = Column(Date)
    due_date = Column(Date)
    amount = Column(Float)
    status = Column(String)

