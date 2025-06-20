from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from datetime import date
from enum import Enum
from typing import Optional
import re

# Phone number validation pattern
PHONE_PATTERN = re.compile(r"^[0-9]{10,15}$")

class CustomerBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    phone_number: str
    email: EmailStr
    address: str

    @field_validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if len(v) < 1 or len(v) > 100:
            raise ValueError("Name must be between 1-100 characters")
        return v

    @field_validator('phone_number')
    def validate_phone(cls, v):
        if not PHONE_PATTERN.match(v):
            raise ValueError("Phone must be 10-15 digits")
        return v

    @field_validator('address')
    def validate_address(cls, v):
        if len(v) > 200:
            raise ValueError("Address too long (max 200 chars)")
        return v

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    customer_id: int

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None

class BillStatus(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    OVERDUE = "overdue"

class BillBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    customer_id: int
    billing_date: date
    due_date: date
    amount: float = Field(..., gt=0)
    status: BillStatus

class BillCreate(BillBase):
    pass

class Bill(BillBase):
    bill_id: int

class BillUpdate(BaseModel):
    customer_id: Optional[int] = None
    billing_date: Optional[date] = None
    due_date: Optional[date] = None
    amount: Optional[float] = Field(None, gt=0)
    status: Optional[BillStatus] = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 4 or len(v) > 50:
            raise ValueError("Username must be 4-50 characters")
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator('role')
    def validate_role(cls, v):
        if v not in ["admin", "operator"]:
            raise ValueError("Role must be 'admin' or 'operator'")
        return v

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    username: str
    role: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
