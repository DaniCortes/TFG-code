import re

from fastapi import HTTPException
from passlib.context import CryptContext


def validate_username(username: str):
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        raise HTTPException(status_code=400, detail="Invalid username format")


def hash_password(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)
