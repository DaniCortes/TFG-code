from fastapi import APIRouter, Depends

from src.controllers.follow_controller import FollowController
from src.services.follow_service import FollowService
from src.utils.token_utils import get_current_user

router = APIRouter()

service = FollowService()
controller = FollowController(service)


@router.get("/followers", response_model=dict, status_code=200)
async def get_followers(current_user_id: str = Depends(get_current_user)):
    followers = await controller.get_followers(current_user_id)
    return {"followers": followers}


@router.get("/following", response_model=dict, status_code=200)
async def get_following(current_user_id: str = Depends(get_current_user)):
    following_users = await controller.get_following(current_user_id)
    return {"following": following_users}


@router.post("/follows/{following_id}", response_model=dict, status_code=201)
async def follow_user(following_id: str, current_user_id: str = Depends(get_current_user)):
    await controller.follow_user(current_user_id, following_id)
    return {"message": "User followed successfully"}


@router.delete("/follows/{unfollowing_id}", response_model=dict, status_code=200)
async def unfollow_user(unfollowing_id: str, current_user_id: str = Depends(get_current_user)):
    await controller.unfollow_user(current_user_id, unfollowing_id)
    return {"message": "User unfollowed successfully"}
