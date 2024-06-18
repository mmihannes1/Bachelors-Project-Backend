import requests
import random
import datetime
from dotenv import load_dotenv
import os

URL = "http://127.0.0.1:8000"

load_dotenv()
header = {"access_token": os.environ.get("API_KEY")}


def ping_application():
    try:
        r = requests.get("http://127.0.0.1:8000")
        if r.status_code == 200:
            return True
    except:
        return False


def add_persons(size):
    """Fill the database with dummy persons"""

    first_names = [
        "Darth",
        "Obi-Wan",
        "Anakin",
        "Leia",
        "Kylo",
        "Boba",
        "Han",
        "Ahsoka",
        "Luke",
    ]

    last_names = [
        "Vader",
        "Kenobi",
        "Skywalker",
        "Organa",
        "Ren",
        "Fett",
        "Solo",
        "Tano",
    ]

    job_role = ["Bartender", "Kock", "Servitör", "Chef", "Hovmästare", "Bagare"]

    for i in range(size):
        data = {
            "first_name": first_names[random.randint(0, len(first_names) - 1)],
            "last_name": last_names[random.randint(0, len(last_names) - 1)],
            "job_role": job_role[random.randint(0, len(job_role) - 1)],
            "birthday": "2024-05-02T20:00:00.000Z",
        }
        response = requests.post(f"{URL}/person", json=data, headers=header)

        if response.status_code == 200:
            print(f"Successfully added person: {i}")


def add_shifts(size):
    """Fill database with dummy shifts"""

    for i in range(size):
        start_time = datetime.datetime(2024, 1, 30, 8, 0, 0)
        end_time = datetime.datetime(2024, 1, 30, 17, 0, 0)

        data = {
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "comment": None,
            "person_id": i,
        }

        response = requests.post(f"{URL}/shift", json=data, headers=header)

        if response.status_code == 200:
            print(f"Successfully added shift: {i}")

    for i in range(size):
        if i % 3 == 0:
            start_time = datetime.datetime(2024, 2, 17, 8, 0, 0)
            end_time = datetime.datetime(2024, 2, 17, 17, 0, 0)

            data1 = {
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "comment": "Jobbade 2 timmar övertid",
                "person_id": i,
            }

            start_time = datetime.datetime(2024, 5, 1, 10, 0, 0)
            end_time = datetime.datetime(2024, 5, 1, 19, 0, 0)

            data2 = {
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "comment": "Bytte pass med Anakin",
                "person_id": i,
            }

            start_time = datetime.datetime(2024, 4, 5, 18, 0, 0)
            end_time = datetime.datetime(2024, 4, 5, 2, 0, 0)

            data3 = {
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "comment": None,
                "person_id": i,
            }

            response1 = requests.post(f"{URL}/shift", json=data1, headers=header)
            response2 = requests.post(f"{URL}/shift", json=data2, headers=header)
            response3 = requests.post(f"{URL}/shift", json=data3, headers=header)

            if response1.status_code == 200:
                print(f"Successfully added shift: {i}")

            if response2.status_code == 200:
                print(f"Successfully added shift: {i}")

            if response3.status_code == 200:
                print(f"Successfully added shift: {i}")


def add_overtime(size):
    """Fill every 4th shift in the database with dummy overtimes"""
    for i in range(size):
        if i % 4 == 0:

            data = {"type": "Kompledigt", "hours": random.randint(1, 4), "shift_id": i}

            response = requests.post(f"{URL}/overtime", json=data, headers=header)

            if response.status_code == 200:
                print(f"Successfully added overtime: {i}")


if __name__ == "__main__":
    if ping_application():
        size = int(input("Enter size of database:"))
        add_persons(size)
        add_shifts(size)
        # add_overtime(size) # TODO Remove overtime associated with shifts when a shift is deleted.
        print("Done")
    else:
        print("The application is not running, start it and try again")
