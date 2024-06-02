from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Base, Subscription, SessionLocal, engine
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List
from auth import authenticate_user, create_access_token, get_current_active_user, Token

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



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
