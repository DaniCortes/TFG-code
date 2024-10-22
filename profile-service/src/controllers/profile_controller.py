from fastapi import HTTPException
from models.profile_update_model import ProfileUpdateRequest
from src.services.profile_service import ProfileService
from src.models.user_model import User
from tortoise.exceptions import DoesNotExist


class ProfileController:
    def __init__(self):
        self.service = ProfileService()

    async def update_profile(self, current_user: User, updates: ProfileUpdateRequest):
        try:
            updated_user = await self.service.update_profile(current_user, updates.model_dump(exclude_unset=True))
            return updated_user
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
