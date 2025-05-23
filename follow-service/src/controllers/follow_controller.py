from fastapi import HTTPException
from src.services.follow_service import FollowService


class FollowController:
    def __init__(self, follow_service: FollowService):
        self.service = follow_service

    async def follow_user(self, user_id: str, following_id: str):
        try:
            return self.service.follow_user(user_id, following_id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def unfollow_user(self, user_id: str, unfollowing_id: str):
        return self.service.unfollow_user(user_id, unfollowing_id)

    async def get_followers(self, user_id: str):
        return self.service.get_followers(user_id)

    async def get_following(self, user_id: str):
        return self.service.get_following(user_id)
