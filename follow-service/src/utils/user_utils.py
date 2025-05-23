import os

import httpx

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")


async def check_user_exists(user_id: str) -> bool:

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_SERVICE_URL}/user/{user_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise e
