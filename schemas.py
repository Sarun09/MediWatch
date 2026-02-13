from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class MedicationCreate(BaseModel):
    name: str
    dosage: str
    frequency: str
    refill_date: str


class MedicationResponse(BaseModel):
    id: int
    name: str
    dosage: str
    frequency: str
    refill_date: str

    class Config:
        from_attributes = True
