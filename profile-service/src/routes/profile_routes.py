from fastapi import APIRouter, Depends
from src.controllers.profile_controller import ProfileController
from src.services.profile_service import ProfileService
from src.models.user_model import User
from src.models.profile_update_model import ProfileUpdateRequest
from src.utils.token_utils import get_current_user

router = APIRouter()
service = ProfileService()
controller = ProfileController(service)


@router.get("/profile", response_model=User)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/profile", response_model=User)
async def update_profile(updates: ProfileUpdateRequest, current_user: User = Depends(get_current_user)):
    return await controller.update_profile(current_user, updates)
