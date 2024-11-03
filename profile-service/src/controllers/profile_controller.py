from fastapi import HTTPException
from src.models.profile_update_model import ProfileUpdateRequest
from src.models.user_model import User
from src.services.profile_service import ProfileService
from tortoise.exceptions import DoesNotExist, IntegrityError
from src.utils.token_utils import generate_token


class ProfileController:
    def __init__(self, profile_service: ProfileService):
        self.service = profile_service

    async def update_profile(self, current_user: User, updates: ProfileUpdateRequest):

        update_token = False

        if updates.username is not None and updates.username != current_user.username:
            update_token = True

        try:
            updated_user = await self.service.update_profile(current_user, updates.model_dump(exclude_unset=True))
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        except IntegrityError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        if update_token:
            updated_user.access_token = await generate_token(str(updated_user.user_id), updated_user.username, updated_user.is_admin)

        return updated_user
