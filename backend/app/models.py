from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    phone_number = Column(String(15), unique=True)
    email = Column(String(100))
    address = Column(String(200))

class Bill(Base):
    __tablename__ = "bills"
    bill_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    billing_date = Column(Date)
    due_date = Column(Date)
    amount = Column(Float)
    status = Column(String(20))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    hashed_password = Column(String(200))
    role = Column(String(20))  # 'admin' or 'operator'
    is_active = Column(Boolean, default=True)
