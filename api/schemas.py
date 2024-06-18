from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Person(BaseModel):
    first_name: str
    last_name: str
    job_role: Optional[str] = None
    birthday: Optional[datetime] = None


class PersonOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    display_tag: str
    created_at: datetime
    updated_at: datetime
    job_role: str | None
    birthday: datetime | None

    field_A: str | None
    field_B: str | None
    field_C: str | None
    field_D: str | None
    field_E: str | None


class Shift(BaseModel):
    start_time: datetime
    end_time: datetime
    person_id: int
    comment: Optional[str] = None


class ShiftOut(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime
    person_id: int
    comment: str | None

    field_A: str | None
    field_B: str | None
    field_C: str | None
    field_D: str | None
    field_E: str | None

    first_name: str
    last_name: str


class Overtime(BaseModel):
    type: str
    hours: int
    shift_id: int


class OvertimeOut(BaseModel):
    type: str
    hours: int
    shift_id: int

    field_A: str | None
    field_B: str | None
    field_C: str | None
    field_D: str | None
    field_E: str | None
