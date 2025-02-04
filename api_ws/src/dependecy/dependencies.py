import uuid
import structlog

from typing import Annotated
from logger import context_logger

from fastapi import (
    HTTPException,
    Depends,
    status
)

from security.securities import (
    oauth2_url,
    decode_token,
    UnauthorizedError
)

from api.user import schemas as user_schemas

def extract_bind_logger() -> structlog.stdlib.BoundLogger:
    
    """
        uuid.uuid4():
        - generate a random uuid
    """
    req_id = str(uuid.uuid4()).replace("-", "")

    logger = context_logger.bind(req_id=f"X-{req_id}")

    return logger

def get_current_user(token: Annotated[str, Depends(oauth2_url)]) -> user_schemas.User:

    try:
        payload = decode_token(token=token)
    except UnauthorizedError as err:
        context_logger.error(f"Failed to decoded token: {str(err)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    
    username = payload.get("sub")

    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials (invalid user)",
                            headers={"WWW-Authenticate": "Bearer"})

    return user_schemas.User(user_name=username)


def allow_all_user(user: Annotated[user_schemas.User, Depends(get_current_user)]):

    """
        accept user role 
    """
    return user