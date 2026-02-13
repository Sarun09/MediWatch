from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta

import models
import schemas
from database import engine, get_db, Base
from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "MediWatch API Running"}


# ======================
# USER REGISTER
# ======================
@app.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


# ======================
# LOGIN
# ======================
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    token = create_access_token({"sub": user.email})

    return {"access_token": token, "token_type": "bearer"}


# ======================
# ADD MEDICATION
# ======================
@app.post("/medications")
def add_medication(
    medication: schemas.MedicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    new_med = models.Medication(
        name=medication.name,
        dosage=medication.dosage,
        frequency=medication.frequency,
        refill_date=medication.refill_date,
        user_id=current_user.id
    )

    db.add(new_med)
    db.commit()
    db.refresh(new_med)

    return new_med


# ======================
# GET USER MEDICATIONS
# ======================
@app.get("/medications")
def get_medications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    meds = db.query(models.Medication).filter(models.Medication.user_id == current_user.id).all()

    return meds


# ======================
# UPDATE MEDICATION
# ======================
@app.put("/medications/{med_id}")
def update_medication(
    med_id: int,
    medication: schemas.MedicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    med = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.user_id == current_user.id
    ).first()

    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")

    med.name = medication.name
    med.dosage = medication.dosage
    med.frequency = medication.frequency
    med.refill_date = medication.refill_date

    db.commit()

    return {"message": "Medication updated"}


# ======================
# DELETE MEDICATION
# ======================
@app.delete("/medications/{med_id}")
def delete_medication(
    med_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    med = db.query(models.Medication).filter(
        models.Medication.id == med_id,
        models.Medication.user_id == current_user.id
    ).first()

    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")

    db.delete(med)
    db.commit()

    return {"message": "Medication deleted"}


# ======================
# MEDICATION REMINDERS
# ======================
@app.get("/medications/reminders")
def medication_reminders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    meds = db.query(models.Medication).filter(
        models.Medication.user_id == current_user.id
    ).all()

    upcoming_reminders = []

    today = datetime.today().date()
    reminder_limit = today + timedelta(days=7)

    for med in meds:
        try:
            refill_date = datetime.strptime(med.refill_date, "%Y-%m-%d").date()

            if today <= refill_date <= reminder_limit:
                upcoming_reminders.append({
                    "medication": med.name,
                    "refill_date": med.refill_date,
                    "message": "Refill needed soon"
                })

        except:
            pass

    return upcoming_reminders
