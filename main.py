from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Base, Subscription, SessionLocal, engine
from pydantic import BaseModel
from typing import List

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SubscriptionCreate(BaseModel):
    user_id: int
    plan: str

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan: str
    start_date: datetime.datetime
    active: bool

@app.post("/subscriptions/", response_model=SubscriptionResponse)
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@app.get("/subscriptions/", response_model=List[SubscriptionResponse])
def read_subscriptions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    subscriptions = db.query(Subscription).offset(skip).limit(limit).all()
    return subscriptions
