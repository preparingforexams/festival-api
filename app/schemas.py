from datetime import datetime
from typing import List

from pydantic import BaseModel

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


class Festival(FestivalBase):
    id: int
    start: datetime
    end: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    telegram_id: int
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    festivals: List[Festival]

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

    class Config:
        orm_mode = True
