from datetime import datetime

from pydantic import BaseModel

from . import models
from .models import AttendanceStatus


class FestivalBase(BaseModel):
    name: str
    start: str
    end: str
    link: str | None = None


class FestivalCreate(FestivalBase):
    class Config:
        orm_mode = True


class FestivalSearchQuery(BaseModel):
    name: str
    score_threshold: int = 70


date_format = "%d.%m"


class Festival(FestivalBase):
    id: int
    start: datetime
    end: datetime

    class Config:
        orm_mode = True

    @classmethod
    def from_model(cls, model: models.Festival):
        cls.name = model.name
        cls.start = model.start
        cls.end = model.end
        cls.link = model.link
        cls.id = model.id

        return cls(
            id=model.id,
            name=model.name,
            start=model.start,
            end=model.end,
            link=model.link,
        )


class UserBase(BaseModel):
    telegram_id: int
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    class Config:
        orm_mode = True


class FestivalAttendeeBase(BaseModel):
    festival_id: int
    status: AttendanceStatus = AttendanceStatus.NO


class FestivalAttendeeCreate(FestivalAttendeeBase):
    pass


class FestivalAttendeeUpdate(FestivalAttendeeBase):
    pass


class FestivalAttendee(FestivalAttendeeBase):
    id: int
    user_id: int
    festival: Festival

    @classmethod
    def from_db(cls, attendee: models.FestivalAttendee, festival: models.Festival) -> "FestivalAttendee":
        return cls(
            festival_id=festival.id,
            status=AttendanceStatus(attendee.status),
            id=attendee.id,
            user_id=attendee.user_id,
            festival=Festival.from_model(festival)
        )

    class Config:
        orm_mode = True
