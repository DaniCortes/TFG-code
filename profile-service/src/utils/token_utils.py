from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import httpx
from src.models.user_model import User
from tortoise.exceptions import DoesNotExist

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://auth-service:8000/tokens")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://auth-service:8000/users/me", headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            user_data = response.json()
            user = await User.get(user_id=user_data['user_id'])
            return user
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        except httpx.HTTPStatusError:
            detail = response.json().get("detail")
            raise HTTPException(
                status_code=response.status_code, detail=detail)
