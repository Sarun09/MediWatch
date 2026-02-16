from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import models


# ------------------------------
# Reminder Check Function
# ------------------------------
def check_medication_reminders():

    db: Session = SessionLocal()

    try:
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)

        medications = db.query(models.Medication).all()

        for med in medications:

            if med.refill_date:

                refill_date = med.refill_date

                # Reminder if refill is tomorrow
                if refill_date == tomorrow:
                    print(f"⚠️ Reminder: {med.name} refill is tomorrow for user {med.user_id}")

                # Reminder if refill is today
                if refill_date == today:
                    print(f"🚨 URGENT: {med.name} refill is TODAY for user {med.user_id}")

    finally:
        db.close()


# ------------------------------
# Scheduler Setup
# ------------------------------
scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.add_job(
        check_medication_reminders,
        "interval",
        minutes=1   # Change later (testing mode)
    )

    scheduler.start()
