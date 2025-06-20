from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, SessionLocal, Base
from passlib.context import CryptContext
from datetime import timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create default admin on startup
@app.on_event("startup")
def create_admin():
    db = SessionLocal()
    if not crud.get_user_by_username(db, "admin"):
        admin = schemas.UserCreate(
            username="admin",
            password="admin123",
            role="admin"
        )
        crud.create_user(db, admin)
    db.close()



def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = crud.get_user_by_username(db, username=token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Bills
@app.post("/bills/", response_model=schemas.Bill)
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    return crud.create_bill(db=db, bill=bill)

@app.get("/bills/", response_model=list[schemas.Bill])
def read_bills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Allow both admin and operator to view bills
    return crud.get_bills(db, skip=skip, limit=limit)

@app.get("/bills/{bill_id}", response_model=schemas.Bill)
def read_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Allow both admin and operator to view specific bill
    db_bill = crud.get_bill(db, bill_id)
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill


@app.delete("/bills/{bill_id}", response_model=schemas.Bill)
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    return crud.delete_bill(db, bill_id)

@app.put("/bills/{bill_id}", response_model=schemas.Bill)
def update_bill(
    bill_id: int,
    bill_update: schemas.BillUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update")
    db_bill = crud.update_bill(db, bill_id, bill_update)
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return db_bill

@app.get("/users/me", response_model=schemas.User)
def read_current_user(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, username=current_user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Auth endpoints
@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": user.username,  # Using username as token for simplicity
        "token_type": "bearer"
    }





# Protected Customer Endpoints
# Customer endpoints
@app.post("/customers/", response_model=schemas.Customer)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "operator"]:
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    try:
        return crud.create_customer(db=db, customer=customer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while creating customer: {str(e)}"
        )


@app.get("/customers/", response_model=list[schemas.Customer])
def read_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Allow both admin and operator to view customers
    return crud.get_customers(db, skip=skip, limit=limit)

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Allow both admin and operator to view specific customer
    db_customer = crud.get_customer(db, customer_id)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# Admin-only Endpoints
@app.delete("/customers/{customer_id}", response_model=schemas.Customer)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete")
    
    # Get customer first to return it in the response
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Perform the delete operation
    crud.delete_customer(db, customer_id)
    return customer


@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(
    customer_id: int,
    customer_update: schemas.CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update")
    db_customer = crud.update_customer(db, customer_id, customer_update)
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# User Management
@app.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create users")
    return crud.create_user(db=db, user=user)
