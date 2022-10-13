import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user"

    telegram_id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    festivals = relationship("Festival", secondary="festivalattendee")

    def __str__(self):
        return self.name


class Festival(Base):
    __tablename__ = "festival"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    link = Column(String, unique=True, nullable=True)

    date_format = "%d.%m"

    def __str__(self):
        start = self.start.strftime(self.date_format)
        end = self.start.strftime(self.date_format)
        link = f" {self.link}" if self.link else ""

        return f"{self.name} ({start} - {end}){link}"


class AttendanceStatus(enum.Enum):
    NO = 0
    MAYBE = 1
    YES = 2
    HAS_TICKET = 3

    def __str__(self):
        result = "not attending"

        match self:
            case AttendanceStatus.MAYBE:
                result = "maybe"
            case AttendanceStatus.YES:
                result = "attending"
            case AttendanceStatus.HAS_TICKET:
                result = "has ticket"

        return result


class FestivalAttendee(Base):
    __tablename__ = "festivalattendee"
    __table_args__ = (UniqueConstraint('festival_id', 'user_id', name='attendee_single_status_constraint'),)

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    festival_id = Column(Integer, ForeignKey(f"{Festival.__tablename__}.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey(f"{User.__tablename__}.telegram_id"), index=True, nullable=False)
    status = Column(Integer, Enum(AttendanceStatus), nullable=False)
