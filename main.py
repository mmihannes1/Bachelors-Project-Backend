"""
Main file for initializing Fast-api app.
"""

from fastapi import FastAPI
from api.database import engine
from api import models
from api.routers import overtime, person, shift
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

add_pagination(app)

# Allowing CORS see documentation at https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def hello_world():
    return "Hello World!"


app.include_router(person.router)
app.include_router(shift.router)
app.include_router(overtime.router)
