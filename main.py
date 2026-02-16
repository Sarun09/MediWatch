from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import schemas
from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from fastapi.security import OAuth2PasswordRequestForm
from datetime import date, timedelta
from scheduler import start_scheduler

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Start scheduler when app starts
@app.on_event("startup")
def startup_event():
    start_scheduler()


@app.get("/")
def home():
    return {"message": "MediWatch API Running"}



# ========================
# USER REGISTER
# ========================
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


# ========================
# LOGIN
# ========================
@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


# ========================
# PROTECTED TEST ROUTE
# ========================
@app.get("/protected")
def protected_route(current_user: models.User = Depends(get_current_user)):
    return {"message": f"Welcome {current_user.email}"}


# ========================
# ADD MEDICATION
# ========================
@app.post("/medications")
def add_medication(
    medication: schemas.MedicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    new_med = models.Medication(
        name=medication.name,
        dosage=medication.dosage,
        frequency=medication.frequency,
        refill_date=medication.refill_date,
        user_id=current_user.id,
    )

    db.add(new_med)
    db.commit()
    db.refresh(new_med)

    return new_med


# ========================
# GET USER MEDICATIONS
# ========================
@app.get("/medications")
def get_medications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    meds = db.query(models.Medication).filter(
        models.Medication.user_id == current_user.id
    ).all()

    return meds


# ========================
# REMINDER ENDPOINT
# ========================
@app.get("/medications/reminders")
def get_reminders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    today = date.today()
    upcoming = today + timedelta(days=7)

    meds = (
        db.query(models.Medication)
        .filter(
            models.Medication.user_id == current_user.id,
            models.Medication.refill_date <= upcoming,
            models.Medication.refill_date >= today,
        )
        .all()
    )

    return meds
