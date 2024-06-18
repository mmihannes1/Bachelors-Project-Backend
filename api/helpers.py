from datetime import datetime, time
from typing import List, Optional
from api import models
from sqlalchemy import func, and_, or_
import random
from api.models import Person
from dependencies import get_db
from sqlalchemy.orm import Session, Query
from fastapi import Depends, HTTPException


def generate_display_tag(person: Person, db: Session = Depends(get_db)) -> str:
    """Generate a unique display_tag"""
    prefix = person.first_name[0:3] + person.last_name[0:2]
    suffix = random.randint(100, 999)
    tag = prefix.lower() + str(suffix)

    while tag in db.query(models.Person.display_tag).all():
        prefix = person.first_name[0:3] + person.last_name[0:2]
        suffix = random.randint(100, 999)
        tag = prefix + str(suffix)

    return tag


def person_search(search_string: str, db: Session = Depends(get_db)) -> Query:
    """Returns a search query for a provided search string"""
    pattern = f"%{search_string}%"
    if " " in search_string:
        # If the search_string contains a space, assume it's 'first_name last_name'
        # Ignore the rest of the names in search.
        first_name, last_name = search_string.split(" ")[:2]
        query = db.query(models.Person).filter(
            and_(
                func.lower(models.Person.first_name).like(
                    func.lower(f"%{first_name}%")
                ),
                func.lower(models.Person.last_name).like(func.lower(f"%{last_name}%")),
            )
        )
    else:
        query = db.query(models.Person).filter(
            or_(
                func.lower(models.Person.first_name).like(func.lower(pattern)),
                func.lower(models.Person.last_name).like(func.lower(pattern)),
            )
        )

    return query


def shift_join_with_shift_id(shift_id: int, db) -> dict[str:str]:
    """Joins tables of Shifts and Persons to be able to get the person name
    for the person associated with the Shift"""
    shift_query = (
        db.query(models.Shift, models.Person)
        .join(models.Person, models.Shift.person_id == models.Person.id)
        .filter(models.Shift.id == shift_id)
    )

    shift_with_person = shift_query.first()

    if shift_with_person:
        shift, person = shift_with_person
        joined_shift_dict = {
            "id": shift.id,
            "start_time": shift.start_time,
            "end_time": shift.end_time,
            "comment": shift.comment,
            "person_id": shift.person_id,
            "created_at": shift.created_at,
            "updated_at": shift.updated_at,
            "field_A": shift.field_A,
            "field_B": shift.field_B,
            "field_C": shift.field_C,
            "field_D": shift.field_D,
            "field_E": shift.field_E,
            "first_name": person.first_name,
            "last_name": person.last_name,
        }

        return joined_shift_dict


def shift_join_with_person_id(
    person_id: int,
    db,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: Optional[str] = None,  # new parameter to specify sorting attribute
    order_type: Optional[str] = "asc",
) -> List[dict]:
    """Joins tables of Shifts and Persons to be able to get the person name for
    the person associated with the Shift. Returns a list of all shifts associated with the person
    """
    shift_query = (
        db.query(models.Shift, models.Person)
        .join(models.Person, models.Shift.person_id == models.Person.id)
        .filter(models.Shift.person_id == person_id)
    )

    shift_query = apply_date_filters(
        shift_query, start_date=start_date, end_date=end_date
    )

    if sort_by == "start_time":
        shift_query = sort_query_by(shift_query, models.Shift.start_time, order_type)

    shift_with_person = shift_query.all()

    shifts = []
    if shift_with_person:
        for shift, person in shift_with_person:
            joined_shift_dict = {
                "id": shift.id,
                "start_time": shift.start_time,
                "end_time": shift.end_time,
                "comment": shift.comment,
                "person_id": shift.person_id,
                "created_at": shift.created_at,
                "updated_at": shift.updated_at,
                "field_A": shift.field_A,
                "field_B": shift.field_B,
                "field_C": shift.field_C,
                "field_D": shift.field_D,
                "field_E": shift.field_E,
                "first_name": person.first_name,
                "last_name": person.last_name,
            }
            shifts.append(joined_shift_dict)

    return shifts


def sort_query_by(query: Query, attribute, order_type):
    """Sorts the shift query by the given attribute and order_type"""
    if attribute:
        if order_type == "asc":
            query = query.order_by(attribute.asc())
        elif order_type == "desc":
            query = query.order_by(attribute.desc())
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Order type is either asc or desc, you entered {order_type}",
            )
    return query


def apply_date_filters(
    query: Query, start_date: Optional[datetime], end_date: Optional[datetime]
) -> Query:
    """Applies date filters to the shift query"""
    if start_date:
        start_of_day = datetime.combine(start_date, time.min)
        query = query.filter(models.Shift.start_time >= start_of_day)
    if end_date:
        end_of_day = datetime.combine(end_date, time.max)
        query = query.filter(models.Shift.start_time <= end_of_day)
    return query
