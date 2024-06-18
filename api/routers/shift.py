from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import ShiftOut, Shift
from api import models
from dependencies import get_api_key, get_db
from sqlalchemy.orm import Session, aliased
from fastapi_pagination.links import Page
from typing import Optional, Dict
from fastapi_pagination import paginate
from api.helpers import (
    apply_date_filters,
    person_search,
    shift_join_with_shift_id,
    sort_query_by,
)

router = APIRouter(
    prefix="/shift",
    tags=["Shift"],
    dependencies=[Depends(get_api_key)],
    responses={404: {"description": "Not found"}},
)


@router.post("")
async def create_shift(shift: Shift, db: Session = Depends(get_db)) -> Shift:
    """Create a new shift for a person and adds it to the database"""
    if shift.start_time > shift.end_time:
        raise HTTPException(
            status_code=400, detail="End time cannot be before start time"
        )

    db_shift = models.Shift(
        start_time=shift.start_time,
        end_time=shift.end_time,
        comment=shift.comment,
        person_id=shift.person_id,
    )
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return shift


@router.get("")
async def get_all_shifts(
    db: Session = Depends(get_db),
    order_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    search_string: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Page[ShiftOut]:
    """Get shifts from the database"""
    if search_string:
        query = person_search(search_string, db)
    else:
        query = db.query(models.Person)

    # Create a subquery to select the first name and id from the Person table
    subquery = query.with_entities(models.Person.id, models.Person.first_name).subquery()
    person_alias = aliased(models.Person, subquery)

    # Create the main query using the Shift table
    shift_query = (
        db.query(models.Shift)
        .join(
            person_alias, models.Shift.person_id == person_alias.id
        )  # Join with the aliased subquery
        .filter(
            models.Shift.person_id.in_(db.query(person_alias.id))
        )  # Filter to include only those in the subquery
    )

    if sort_by == "first_name":
        shift_query = sort_query_by(shift_query, person_alias.first_name, order_type)
    elif sort_by == "start_time":
        shift_query = sort_query_by(shift_query, models.Shift.start_time, order_type)

    shift_query = apply_date_filters(shift_query, start_date, end_date)

    unjoined_shifts = shift_query.all()

    shifts = []
    for shift in unjoined_shifts:
        shift = shift_join_with_shift_id(shift.id, db)
        if shift is not None:
            shifts.append(shift)

    return paginate(shifts)


@router.get("/{shift_id}")
async def get_shift_by_id(shift_id: int, db: Session = Depends(get_db)):
    """Get a shift by shift_id from the database"""
    shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
    if shift:
        joined_shift = shift_join_with_shift_id(shift_id, db)
        if joined_shift:
            return joined_shift
    raise HTTPException(status_code=404, detail="Shift not found")


@router.put("/{shift_id}")
async def update_shift(shift: Shift, shift_id, db: Session = Depends(get_db)) -> Shift:
    """Update a shift in the database"""
    s = db.query(models.Shift).filter(models.Shift.id == shift_id).first()

    if shift.start_time > shift.end_time:
        raise HTTPException(
            status_code=400, detail="End time cannot be before start time"
        )

    if s:
        db.query(models.Shift).filter(models.Shift.id == shift_id).update(
            {
                "start_time": shift.start_time,
                "end_time": shift.end_time,
                "comment": shift.comment,
            }
        )
        db.commit()
        return shift
    raise HTTPException(status_code=404, detail="Shift not found")


@router.delete("/{shift_id}")
async def delete_shift(shift_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Delete a shift from the database"""
    s = db.query(models.Shift).filter(models.Shift.id == shift_id).first()

    if s:
        db.query(models.Shift).filter(models.Shift.id == shift_id).delete()
        db.commit()
        return {"message": "Shift deleted successfully"}
    raise HTTPException(status_code=404, detail="Shift not found")
