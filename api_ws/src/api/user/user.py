from typing import  List

from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends
)

from repository.user.user import UserRepo
from repository.user.schemas import UserInfo
from repository.exceptions import (
    RepoInternalError,
    BadRequestError
)

from api.user import schemas as user_schemas

from dependecy.dependencies import (
    verify_root_prviliage,
    verify_all_prviliage
)

def init_user_router(user_repo: UserRepo) -> APIRouter:

    user_router = APIRouter(prefix="", tags=["User"])

    """
        {TODO} write down whole process for check authorization
    """

    """
        Dependency Injection means that there is a way for your code
        to declare things that it requires to work and use: "dependencies"

        It is very useful when you need to :
        - Have shared logic
        - Enforce security, authetication, role requirements
        - And other things...

        Depends works a bit different from others, Bodys, Query, and etc.
        You only give a Depends a single parameter, which must be something like function. 
        You do not call it directly, you just pass it as a parameter to Depends().


        Steps:
        When a new request arrives, FastAPI will take care of:
        - Calling your dependecies function with the correct parameters
        - Get the result from your function
        - Assign that result to the parameter in your path operation function

        When you need to use the <function> dependency, you have to write the whole parameter with the type annotation and Depends() like:

        ```
            parameters: Annotated[dict, Depends(<function>)]
        ```

        But because we are using Annotatedm we can store that Annotated value in a variable and use it in multiple places.

        The best part is that the type information will be preserved, 
        which means that your editor will be able to keep providing you with autocompletion, 
        inline errors, etc.
    """


    """
        Dependencies in path operation decorators
        
        In some cases you do not really need the return value of a dependecy inside your path operation function or dependecy does not return a value.
        But you still need it to be executed/solved.

        For those cases, instead of declaring a path operation function parameter with Depends, you can add a list of dependencies to the path operation decorator.
    
        These dependecies will be executed/solved the same way as normal dependencies. But their value
        (if they return any) would not be passed to path operation function
        
    """

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


    @user_router.delete("/v1/users/{user_id}",
                        dependencies=[Depends(verify_root_prviliage)])
    def delete_user(user_id: str):

        try:
            user_repo.delete_user(user_id=user_id)
        except BadRequestError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Could not remove root/admin user")
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to delete user")
        
        return status.HTTP_200_OK
        
    return user_router