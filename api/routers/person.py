from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import Person, PersonOut, ShiftOut
from api import models
from dependencies import get_db, get_api_key
from sqlalchemy.orm import Session
from typing import Optional, Dict
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import paginate as pag
from fastapi_pagination.links import Page
from api.helpers import generate_display_tag, person_search, shift_join_with_person_id

router = APIRouter(
    prefix="/person",
    tags=["Person"],
    dependencies=[Depends(get_api_key)],
    responses={404: {"description": "Not found"}},
)


@router.post("")
async def create_person(
    person: Person,
    db: Session = Depends(get_db),
) -> Person:
    """Create a new person and adds it to the database"""
    first_name = person.first_name
    last_name = person.last_name
    display_tag = generate_display_tag(person, db)

    db_person = models.Person(
        first_name=first_name,
        last_name=last_name,
        display_tag=display_tag,
        job_role=person.job_role,
        birthday=person.birthday,
    )
    db.add(db_person)
    db.commit()
    db.refresh(db_person)

    return person


@router.get("/{person_id}")
async def get_person_by_id(person_id: int, db: Session = Depends(get_db)) -> PersonOut:
    """Get a person by person_id from the database"""
    person = db.query(models.Person).filter(models.Person.id == person_id).first()

    if person:
        return person
    raise HTTPException(status_code=404, detail="Person not found")


@router.get("")
async def get_all_persons(
    search_string: Optional[str] = None,
    order_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Page[PersonOut]:
    """Get persons from the database using regex-like matching on first and/or last name"""
    # main query
    query = db.query(models.Person)

    if search_string:
        query = person_search(search_string, db)

    sort_by_map = {
        "last_name": models.Person.last_name,
        "first_name": models.Person.first_name,
    }

    attribute = sort_by_map.get(sort_by)

    # If attribute is not None, apply the sorting
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
    return paginate(db, query)


@router.put("/{person_id}")
async def update_person(
    person: Person, person_id: int, db: Session = Depends(get_db)
) -> Person:
    """Update a person in the database"""
    p = db.query(models.Person).filter(models.Person.id == person_id).first()

    if p:
        db.query(models.Person).filter(models.Person.id == person_id).update(
            {
                "first_name": person.first_name,
                "last_name": person.last_name,
                "job_role": person.job_role,
                "birthday": person.birthday,
            }
        )
        db.commit()
        return person
    raise HTTPException(status_code=404, detail="Person not found")


@router.get("/{person_id}/shift")
async def get_shifts(
    person_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: Optional[str] = None,
    order_type: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Page[ShiftOut]:
    """Get all shifts for a person from the database"""
    p = db.query(models.Person).filter(models.Person.id == person_id).first()

    if p:
        shifts = shift_join_with_person_id(
            person_id, db, start_date, end_date, sort_by, order_type
        )
        return pag(shifts)
    raise HTTPException(status_code=404, detail="Person not found")


@router.delete("/{person_id}")
async def delete_person(
    person_id: int, db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Delete a person along with their shifts (if any) from the database"""
    p = db.query(models.Person).filter(models.Person.id == person_id).first()

    if p:
        db.query(models.Shift).filter(models.Shift.person_id == person_id).delete()
        db.query(models.Person).filter(models.Person.id == person_id).delete()
        db.commit()
        return {"message": "Person deleted successfully"}
    raise HTTPException(status_code=404, detail="Person not found")
