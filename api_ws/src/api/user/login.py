import structlog
import datetime

from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException
)

from fastapi.security import OAuth2PasswordRequestForm

from repository.user.user import UserRepo
from repository.user.schemas import UserInfo
from repository.exceptions import RepoInternalError

from security.securities import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    generate_access_token
)

from api.user import schemas as user_schemas


def init_login_router(user_repo: UserRepo) -> APIRouter:

    login_router = APIRouter(prefix="", tags=["Login"])

    """
        OAuth2:
        - OAuth2 is a specification that defines several ways to handle authentication and authorization.

        OpenAPI (previously known as Swagger) is the open specification for building APIs.

        FastAPI is based on OpenAPI. OpenAPI has a way to define multiple security "schemes".
        By using them, you can take advantage of all these standard-based tools, including these interactive documentation systems.

        OpenAPI defines the following security schemas:

        - apiKey: an application specific key that can come from:
          1. A query parameter
          2. A header
          3. A cookie.

        - http: standard HTTP authentication systems, including:
          1. bearer: a header Authorization with a value of Bearer plus a token. This is inherited from OAuth2.
          2. HTTP Basic authentication
          3. HTTP Digest, etc.

        - oauth2: all the OAuth2 ways to handle security
          1. Serveral of these flows are appropriate for building an OAuth 2.0
             authentication provider (like Google, Facebook, Twitter, GitHub, etc):
          2. But there is one specific "flow" that can be perfectly used for handling authentication in the same application directly.
             - password: some next chapters will cover examples of this.
    """

    @login_router.post("/v1/login/access-token",
                       response_model=user_schemas.Token)
    def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        """
          create access token
        """
        try:
            user_info: UserInfo = user_repo.get_user(user_id=form_data.username)
        except RepoInternalError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorrect username")
        
        ## verified password
        verified = verify_password(password=form_data.password,
                                   hashed_password=user_info.hashed_password)
        
        if not verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Incorect password")
        
        access_token = generate_access_token(user_id=user_info.user_id,
                                             expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

        return user_schemas.Token(access_token=access_token,
                                  token_type="bearer")

    return login_router