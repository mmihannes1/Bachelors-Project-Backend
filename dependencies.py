from api.database import SessionLocal
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv
import os


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


load_dotenv()

api_key_header = APIKeyHeader(name="access_token", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Check API key otherwise return a 403 error"""
    if api_key_header == os.environ.get("API_KEY"):
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )
