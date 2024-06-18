from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, column_property
from .database import Base
from datetime import datetime


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(35))
    last_name = Column(String(35))
    job_role = Column(String(35))
    birthday = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    display_tag = Column(String(8), unique=True)

    # Dummy data fields
    field_A = Column(String(35))
    field_B = Column(String(35))
    field_C = Column(String(35))
    field_D = Column(String(35))
    field_E = Column(String(35))


class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    time_worked = column_property(end_time - start_time, deferred=True)
    comment = Column(String(100), nullable=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Dummy data fields
    field_A = Column(String(35))
    field_B = Column(String(35))
    field_C = Column(String(35))
    field_D = Column(String(35))
    field_E = Column(String(35))

    person = relationship("Person", backref="shifts")


class Overtime(Base):
    __tablename__ = "overtimes"
    shift_id = Column(
        Integer, ForeignKey("shifts.id"), primary_key=True, nullable=False
    )
    type = Column(String(50), nullable=True)
    hours = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Dummy data fields
    field_A = Column(String(35))
    field_B = Column(String(35))
    field_C = Column(String(35))
    field_D = Column(String(35))
    field_E = Column(String(35))

    shift = relationship("Shift", backref="overtimes")
