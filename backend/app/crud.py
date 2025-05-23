from sqlalchemy.orm import Session
from app import models, schemas

# Customer CRUD
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()

def delete_customer(db: Session, customer_id: int):
    customer = get_customer(db, customer_id)
    if customer:
        db.delete(customer)
        db.commit()
    return customer

# Bill CRUD
def create_bill(db: Session, bill: schemas.BillCreate):
    db_bill = models.Bill(**bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

def get_bills(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Bill).offset(skip).limit(limit).all()

def get_bill(db: Session, bill_id: int):
    return db.query(models.Bill).filter(models.Bill.bill_id == bill_id).first()

def delete_bill(db: Session, bill_id: int):
    bill = get_bill(db, bill_id)
    if bill:
        db.delete(bill)
        db.commit()
    return bill

