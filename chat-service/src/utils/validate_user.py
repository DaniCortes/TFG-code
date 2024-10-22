import os
import httpx


async def validate_user(self, token: str) -> dict:
    AUTH_SERVICE_URL = os.getenv(
        "AUTH_SERVICE_URL", "http://auth-service:8000/users/me")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            AUTH_SERVICE_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()
