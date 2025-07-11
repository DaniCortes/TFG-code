import os

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from src.models.user_model import User

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{AUTH_SERVICE_URL}/tokens")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            user_data = response.json()

            return User(**user_data)

        except httpx.HTTPError as e:
            if e.response.status_code == 401:
                raise HTTPException(
                    status_code=401, detail="Invalid authentication credentials")
            elif e.response.status_code == 403:
                raise HTTPException(status_code=403, detail="Access forbidden")
            elif e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
        except httpx.HTTPStatusError:
            detail = response.json().get("detail")
            raise HTTPException(
                status_code=response.status_code, detail=detail)
