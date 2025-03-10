import os

import httpx
from fastapi import HTTPException

from src.models.user_model import User

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")


async def validate_user(token: str) -> User:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            user_data = response.json()
            user = User(user_id=user_data['user_id'],
                        username=user_data['username'],
                        is_admin=user_data['is_admin'])
            return user

        except httpx.HTTPStatusError:
            detail = response.json().get("detail")
            raise HTTPException(
                status_code=response.status_code, detail=detail)
