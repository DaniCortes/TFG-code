from fastapi import HTTPException

from src.services.follow_service import FollowService
from src.utils.user_utils import check_user_exists


class FollowController:
    def __init__(self, follow_service: FollowService):
        self.service = follow_service

    async def follow_user(self, user_id: str, following_id: str):
        if not await check_user_exists(following_id):
            raise HTTPException(status_code=404, detail="User not found")

        try:
            return await self.service.follow_user(user_id, following_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Internal server error: " + str(e))

    async def unfollow_user(self, user_id: str, unfollowing_id: str):

        try:
            return await self.service.unfollow_user(user_id, unfollowing_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_follows(self, user_id: str):
        return await self.service.get_follows(user_id)
