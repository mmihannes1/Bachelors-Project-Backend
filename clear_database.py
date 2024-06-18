from api import models
from api.database import SessionLocal

"""File for clearing database"""


def delete_records():
    """Delete all records in the local database"""
    db = SessionLocal()
    try:
        db.query(models.Overtime).delete()
        db.query(models.Shift).delete()
        db.query(models.Person).delete()
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    delete_records()
    print("Database cleared successfully...")
