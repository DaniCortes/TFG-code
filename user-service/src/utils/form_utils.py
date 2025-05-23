import re

from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_username(username: str):
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        raise HTTPException(status_code=400, detail="Invalid username format")


def hash_password(password: str):
    return pwd_context.hash(password)


def check_password(plain_password: str, hashed_password: str):
    if not pwd_context.verify(plain_password, hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return True
