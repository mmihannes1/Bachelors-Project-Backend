from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

engine = None

if "NAMESPACE" in os.environ and os.environ["NAMESPACE"] == "heroku":
    uri = os.environ["DATABASE_URL"]
    if uri and uri.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = uri.replace("postgres://", "postgresql://", 1)
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
