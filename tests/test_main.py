"""
Test file for handling valid and invalid requests made to the database.
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from api.database import Base
from main import app
from dotenv import load_dotenv
from dependencies import get_db
import os
from fastapi_pagination import add_pagination

# Note that the name of the function needs to start with 'test' for it to be included in the pytest
# To ensure the database is filled correctly, put your test function alongside the according http-type(Get, Post, etc.)

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
add_pagination(app)
client = TestClient(app)

load_dotenv()
header = {"access_token": os.environ.get("API_KEY")}


def test_hello_world():
    """Test hello world endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Hello World!"


# -------------- Post ---------------


def test_valid_post_person():
    """Test for creating a person"""
    data = {
        "first_name": "Anders",
        "last_name": "Postman",
        "job_role": None,
        "birthday": None,
    }
    response = client.post("/person", json=data, headers=header)
    assert response.status_code == 200
    assert response.json() == data


def test_invalid_post_person():
    """Test for creation of person with invalid data/datatypes
    Should give error after a certain character limit?"""
    data = {"first_name": 5, "last_name": False}
    response = client.post("/person", json=data, headers=header)
    assert response.status_code == 422


def test_valid_post_shift():
    """Test for creation of shift"""
    data = {
        "start_time": "2024-02-17T18:39:00",
        "end_time": "2024-02-17T20:39:00",
        "comment": "work",
        "person_id": 1,
    }
    response = client.post("/shift", json=data, headers=header)
    assert response.status_code == 200
    assert response.json() == data


def test_post_shift_end_time_before_start_time():
    """Test for creation of shift"""
    data = {
        "start_time": "2024-02-17T18:39:00",
        "end_time": "2024-01-17T20:39:00",
        "comment": "work",
        "person_id": 1,
    }
    response = client.post("/shift", json=data, headers=header)
    assert response.status_code == 400
    assert response.json() == {"detail": "End time cannot be before start time"}


def test_valid_post_overtime():
    """Test for creation of overtime"""
    data = {"shift_id": 1, "type": "Fix issues", "hours": 1}
    response = client.post("/overtime", json=data, headers=header)
    assert response.status_code == 200
    assert response.json() == data


def test_invalid_post_overtime():
    """Test for creation of overtime"""
    data = {"shift_id": 123456, "type": "Fix issues", "hours": 1}
    response = client.post("/overtime", json=data, headers=header)
    assert response.status_code == 200
    assert response.json() == data


# --------------- Put ---------------


def test_valid_put_person():
    """Test for editing name of existing person"""
    data = {
        "first_name": "Peter",
        "last_name": "Postman",
        "job_role": None,
        "birthday": None,
    }
    response = client.put("/person/1", json=data, headers=header)
    assert response.status_code == 200
    assert response.json() == data


def test_invalid_put_person():
    """Test for editing name of person with invalid person ID"""
    data = {"first_name": "Lars", "last_name": "Olof"}
    response = client.put("/person/123456", json=data, headers=header)
    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_valid_put_shift():
    """Test for editing of existing shift"""
    data = {
        "start_time": "2024-02-17T20:39:00",
        "end_time": "2024-02-17T22:39:00",
        "comment": "code",
        "person_id": 1,
    }
    response = client.put("/shift/1", json=data, headers=header)
    assert response.status_code == 200
    assert response.json() == data


def test_put_sift_end_before_start():
    """Test for editing of existing shift"""
    data = {
        "start_time": "2024-02-17T20:39:00",
        "end_time": "2024-01-17T22:39:00",
        "comment": "code",
        "person_id": 1,
    }
    response = client.put("/shift/1", json=data, headers=header)
    assert response.status_code == 400
    assert response.json() == {"detail": "End time cannot be before start time"}


def test_invalid_put_shift():
    """Test for editing of non-existing shift"""
    data = {
        "start_time": "2024-02-17T20:39:00",
        "end_time": "2024-02-17T22:39:00",
        "comment": "code",
        "person_id": 1,
    }
    response = client.put("/shift/123456", json=data, headers=header)
    assert response.status_code == 404
    assert response.json() == {"detail": "Shift not found"}


# ------------------ Get -------------


def test_valid_get_person():
    response = client.get("/person/1", headers=header)
    assert response.status_code == 200


def test_valid_get_shift():
    response = client.get("/shift/1", headers=header)
    assert response.status_code == 200


def test_invalid_get_shift():
    response = client.get("/shift/99", headers=header)
    assert response.status_code == 404


def test_valid_get_persons():
    response = client.get("/person")
    assert response.status_code == 403

    response = client.get("/person", headers=header)
    assert response.status_code == 200


def test_valid_get_shift_from_person():
    """Test for retrieving existing shifts from a person"""
    response = client.get("/person/1/shift", headers=header)
    shift = response.json()["items"]
    assert shift[0]["first_name"] == "Peter"
    assert shift[0]["last_name"] == "Postman"
    assert response.status_code == 200


def test_valid_get_shifts():
    """Test for retrieving list of existing shifts"""
    response = client.get("/shift", headers=header)
    assert response.status_code == 200


def test_valid_get_shift_by_name():
    response = client.get("shift?search_string=Boba")
    assert response.status_code == 403

    data1 = {
        "first_name": "Bob",
        "last_name": "Postman",
        "job_role": None,
        "birthday": None,
    }
    response1 = client.post("/person", json=data1, headers=header)

    data2 = {
        "first_name": "Alice",
        "last_name": "Test",
        "job_role": None,
        "birthday": None,
    }
    response2 = client.post("/person", json=data2, headers=header)

    assert response1.status_code == 200
    assert response1.json() == data1

    assert response2.status_code == 200
    assert response2.json() == data2

    data3 = {
        "start_time": "2024-02-17T18:39:00",
        "end_time": "2024-02-17T20:39:00",
        "comment": "work",
        "person_id": 1,
    }
    response3 = client.post("/shift", json=data3, headers=header)
    assert response3.status_code == 200
    assert response3.json() == data3

    data4 = {
        "start_time": "2024-02-17T18:39:00",
        "end_time": "2024-02-17T20:39:00",
        "comment": "work",
        "person_id": 1,
    }
    response4 = client.post("/shift", json=data4, headers=header)
    assert response4.status_code == 200
    assert response4.json() == data4

    response = client.get("shift?search_string=Postman", headers=header)
    assert response.status_code == 200

    json_response = response.json()
    items_list = json_response.get("items", [])
    for shift in items_list:
        assert shift['last_name'] == 'Postman'


def test_invalid_get_person_by_id():
    response = client.get("person/123456", headers=header)
    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_invalid_get_shift_by_person_id():
    response = client.get("person/123456/shift", headers=header)
    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_valid_get_person_by_name():
    response = client.get("person?search_string=Anders%20Postman")
    assert response.status_code == 403

    response = client.get("person?search_string=Peter%20Postman", headers=header)
    assert response.status_code == 200

    json_response = response.json()
    items_list = json_response.get("items", [])
    assert len(items_list) >= 1, "Items list is empty"


def test_invalid_get_person_by_name():
    response = client.get("/person?search_string=NotExisting")
    assert response.status_code == 403

    response = client.get("person?search_string=Notmatchinganything", headers=header)
    assert response.status_code == 200
    json_response = response.json()
    items_list = json_response.get("items", [])
    assert len(items_list) == 0, "Returned items even though no match should exist"


# TODO check that the names are sorted in the right order
def test_valid_get_person_order():
    response_asc = client.get("/person?sort_by=asc", headers=header)
    response_desc = client.get("/person?sort_by=desc", headers=header)
    assert response_asc.status_code == 200
    assert response_desc.status_code == 200


def test_valid_get_all_overtimes():
    response = client.get("/overtime")
    assert response.status_code == 403

    response = client.get("/overtime", headers=header)
    assert response.status_code == 200


def test_valid_get_overtime_by_shift_id():
    response = client.get("/overtime/1")
    assert response.status_code == 403

    response = client.get("/overtime/1", headers=header)
    assert response.status_code == 200


def test_invalid_get_overtime_by_shift_id():
    response = client.get("/overtime/123456")
    assert response.status_code == 403

    response = client.get("/overtime/123456", headers=header)
    assert response.status_code == 404
    assert response.json() == {"detail": "Shift not found"}


# --------------- Delete -----------------


def test_valid_delete_person():
    """Test for deletion of existing person"""
    shift_data1 = {
        "start_time": "2024-02-17T18:39:00",
        "end_time": "2024-02-17T20:39:00",
        "comment": "test1",
        "person_id": 1,
    }

    shift_data2 = {
        "start_time": "2024-02-17T18:39:00",
        "end_time": "2024-02-17T20:39:00",
        "comment": "test2",
        "person_id": 1,
    }
    client.post("/shift", json=shift_data1, headers=header)
    client.post("/shift", json=shift_data2, headers=header)

    response = client.get("/person/1/shift", headers=header)
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 2

    response = client.delete("/person/1", headers=header)
    assert response.status_code == 200

    response = client.get("/person/1/shift", headers=header)
    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_invalid_delete_person():
    """Test for deletion of non-existing person"""
    response = client.delete("/person/123456", headers=header)
    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}


def test_valid_delete_shift():
    """Test for deletion of shift"""
    person_data = {"first_name": "Hannes", "last_name": "Lundberg"}
    client.post("/person", json=person_data, headers=header)

    shift_data = {
        "start_time": "2024-02-17T18:39:00",
        "end_time": "2024-02-17T20:39:00",
        "comment": "work",
        "person_id": 1,
    }
    client.post("/shift", json=shift_data, headers=header)
    response = client.delete("/shift/1", headers=header)
    assert response.status_code == 200


def test_invalid_delete_shift():
    """Test for deletion of non-existing shift"""
    response = client.delete("/shift/123456", headers=header)
    assert response.status_code == 404
    assert response.json() == {"detail": "Shift not found"}
