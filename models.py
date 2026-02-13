from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    medications = relationship("Medication", back_populates="owner")


class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    dosage = Column(String)
    frequency = Column(String)
    refill_date = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="medications")
