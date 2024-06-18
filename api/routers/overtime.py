from fastapi import APIRouter, Depends, HTTPException
from api.schemas import Overtime, OvertimeOut
from api import models
from dependencies import get_db, get_api_key
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination.links import Page

router = APIRouter(
    prefix="/overtime",
    tags=["Overtime"],
    dependencies=[Depends(get_api_key)],
    responses={404: {"description": "Not found"}},
)


@router.post("")
async def create_overtime(
    overtime: Overtime, db: Session = Depends(get_db)
) -> Overtime:
    """Create overtime for a shift and adds it to the database"""
    db_overtime = models.Overtime(
        type=overtime.type, hours=overtime.hours, shift_id=overtime.shift_id
    )
    db.add(db_overtime)
    db.commit()
    db.refresh(db_overtime)

    return overtime


@router.get("")
async def get_all_overtimes(db: Session = Depends(get_db)) -> Page[OvertimeOut]:
    """Get all overtimes from the database"""
    return paginate(db, select(models.Overtime))


@router.get("/{shift_id}")
async def get_overtime_by_shift(
    shift_id: int, db: Session = Depends(get_db)
) -> list[OvertimeOut]:
    """Get overtime to corresponding shift from the database"""
    shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()

    if shift:
        return (
            db.query(models.Overtime).filter(models.Overtime.shift_id == shift_id).all()
        )
    raise HTTPException(status_code=404, detail="Shift not found")
