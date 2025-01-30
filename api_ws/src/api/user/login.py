import structlog

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status
)

from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer
)

def init_login_router() -> APIRouter:

    login_router = APIRouter(prefix="", tags=["login"])

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

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    @login_router.get("/login")
    def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
        return {"token": token}

    return login_router