import enum

from fastapi import HTTPException
from fuzzywuzzy import fuzz
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .schemas import FestivalAttendee
from .utils import log, parse_date


@log
def get_user(db: Session, telegram_id: int):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()


@log
def get_users(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.User).offset(skip).limit(limit).all()


@log
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(telegram_id=user.telegram_id, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@log
def get_festival(db: Session, festival_id: int):
    return db.query(models.Festival).filter(models.Festival.id == festival_id).first()


@log
def search_festival(db: Session, festival_query: schemas.FestivalSearchQuery):
    festivals = get_festivals(db)
    results = []

    for festival in festivals:
        if fuzz.partial_ratio(festival_query.name, festival.name) > festival_query.score_threshold:
            if fuzz.ratio(festival_query.name, festival.name) == 100:
                results = [festival]
                break
            results.append(festival)

    return results


@log
def get_festival_by_name(db: Session, name: str):
    return db.query(models.Festival).filter(models.Festival.name == name).first()


@log
def get_festivals(db: Session, skip: int = 0, limit: int = 30):
    return db.query(models.Festival).offset(skip).limit(limit).all()


@log
def create_festival(db: Session, festival: schemas.FestivalCreate):
    start = parse_date(festival.start, default_year=2023)
    end = parse_date(festival.end, default_year=2023)

    db_festival = models.Festival(name=festival.name, start=start, end=end, link=festival.link)
    db.add(db_festival)
    db.commit()
    db.refresh(db_festival)

    return db_festival


@log
def attend(db: Session, telegram_id: int, festival: schemas.FestivalAttendeeCreate):
    # noinspection PyTypeChecker
    # no idea why PyCharm thinks that `festival.status.value` is of type `() -> Any`
    status: int = festival.status.value
    db_attendance = models.FestivalAttendee(user_id=telegram_id, festival_id=festival.festival_id, status=status)
    db.add(db_attendance)
    try:
        db.commit()
        db.refresh(db_attendance)
    except IntegrityError as e:
        error_message = "\n".join(e.args)
        if "UNIQUE constraint failed" in error_message:
            raise HTTPException(status_code=400, detail="user already has an attendance status for this festival")
        return None

    return schemas.FestivalAttendee.from_db(db_attendance, get_festival(db, db_attendance.festival_id))


@log
def get_festival_attendee(db: Session, festival_id: int, telegram_id: int):
    return db.query(models.FestivalAttendee).filter(
        models.FestivalAttendee.festival_id == festival_id and models.FestivalAttendee.user_id == telegram_id).first()


@log
def update_attendance(db: Session, telegram_id: int, festival: schemas.FestivalAttendeeUpdate):
    # noinspection PyTypeChecker
    db_festival_attendee = get_festival_attendee(db, festival.festival_id, telegram_id)
    if not db_festival_attendee:
        raise HTTPException(status_code=404, detail="user is not attending this festival")

    if festival.status == models.AttendanceStatus.NO:
        db.delete(db_festival_attendee)
        db.commit()
        return False

    data = festival.dict(exclude_unset=True)
    for key, value in data.items():
        if isinstance(value, enum.Enum):
            value = value.value
        setattr(db_festival_attendee, key, value)

    db.add(db_festival_attendee)
    db.commit()
    db.refresh(db_festival_attendee)

    return schemas.FestivalAttendee.from_db(db_festival_attendee, get_festival(db, db_festival_attendee.festival_id))


@log
def get_festival_attendees(db: Session, telegram_id: int):
    res = db.query(
        models.FestivalAttendee, models.Festival
    ).filter(
        models.FestivalAttendee.user_id == telegram_id
    ).filter(
        models.FestivalAttendee.festival_id == models.Festival.id
    ).all()

    return [FestivalAttendee.from_db(attendee, festival) for attendee, festival in res]
