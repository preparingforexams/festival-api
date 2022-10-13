import os
from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic
from sqlalchemy.orm import Session

from app import crud, schemas
# noinspection PyUnresolvedReferences
# we import Base here so it can be used in alembic/env.py to autogenerate migrations
from app.database import Base, SessionLocal
from app.logger import create_logger
from app.schemas import FestivalAttendeeCreate, FestivalAttendeeUpdate

app = FastAPI()
security = HTTPBasic()

logger = create_logger("festival-api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/v1/user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), credentials=Depends(security)):
    db_user = crud.get_user(db, user.telegram_id)
    if db_user:
        raise HTTPException(400, detail="user with this telegram_id already exists")

    return crud.create_user(db=db, user=user)


@app.post("/v1/festival/", response_model=schemas.Festival)
def create_festival(festival: schemas.FestivalCreate, db: Session = Depends(get_db), credentials=Depends(security)):
    db_festival = crud.get_festival_by_name(db, festival.name)

    if db_festival:
        raise HTTPException(400, detail="festival with this name already exists")

    return crud.create_festival(db=db, festival=festival)


@app.post("/v1/user/{telegram_id}/attend", response_model=schemas.FestivalAttendee)
def attend(telegram_id: int, query: FestivalAttendeeCreate, db: Session = Depends(get_db),
           credentials=Depends(security)):
    db_user = crud.attend(db, telegram_id, query)
    if db_user is None:
        raise HTTPException(status_code=400, detail="error attending this festival")

    return db_user


@app.patch("/v1/user/{telegram_id}/attend", response_model=schemas.FestivalAttendee)
def attend(telegram_id: int, query: FestivalAttendeeUpdate, db: Session = Depends(get_db),
           credentials=Depends(security)):
    db_user = crud.update_attendance(db, telegram_id, query)
    if db_user is None:
        raise HTTPException(status_code=400, detail="error attending this festival")

    return db_user


@app.get("/v1/user/", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip, limit)
    return users


@app.get("/v1/festival/", response_model=List[schemas.Festival])
def get_festivals(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    festivals = crud.get_festivals(db=db, skip=skip, limit=limit)
    return festivals


@app.get("/v1/user/{telegram_id}", response_model=schemas.User)
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, telegram_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")

    return db_user


def main():
    port = os.getenv("APP_PORT")
    port = int(port) if port else 5000
    log_level = os.getenv("APP_LOG_LEVEL", "info").lower()
    logger.setLevel(log_level.upper())

    uvicorn.run("main:app", port=port, log_level=log_level)


if __name__ == "__main__":
    main()
