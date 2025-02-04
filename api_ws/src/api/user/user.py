from typing import  List

from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends
)

from repository.user.user import UserRepo
from repository.user.schemas import UserInfo
from repository.exceptions import RepoInternalError

from api.user import schemas as user_schemas

from dependecy.dependencies import allow_all_user

def init_user_router(user_repo: UserRepo) -> APIRouter:

    user_router = APIRouter(prefix="", tags=["User"])

    """
        {TODO} write down whole process for check authorization
    """

    @user_router.get("/me",
                     dependencies=[Depends(allow_all_user)])
    def get_current_user():
        return status.HTTP_200_OK

    @user_router.get("/v1/users")   
    def get_users_info():

        try:
            users_info: List[UserInfo] = user_repo.get_users()
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Failed to get all users info")

        return user_schemas.UsersInfoResp(users=[user_schemas.UserInfoResp(user_id=user.user_id,
                                                                           user_name=user.user_name,
                                                                           user_role=user.user_role,
                                                                           registered_at=user.registered_at.isoformat()) for user in users_info])

    @user_router.post("/v1/users")
    def register_user(user: user_schemas.RegisterUserReq):

        try:
            result = user_repo.register_user(user_id=user.user_name,
                                             user_name=user.user_name,
                                             password=user.password)
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to register new user")

        return status.HTTP_201_CREATED

    @user_router.get("/v1/users/{user_id}",
                     response_model=user_schemas.UserInfoResp)
    def get_user_info(user_id: str):

        try:
            user_info: UserInfo = user_repo.get_user(user_id=user_id)
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Failed to get {user_id} user info")

        return user_schemas.UserInfoResp(user_id=user_info.user_id,
                                         user_name=user_info.user_name,
                                         user_role=user_info.user_role,
                                         registered_at=user_info.registered_at.isoformat())


    return user_router