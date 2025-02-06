import uuid
import structlog

from enum import Enum

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
    UnauthorizedError,
    AuthenticationLevel
)

def extract_bind_logger() -> structlog.stdlib.BoundLogger:
    
    """
        uuid.uuid4():
        - generate a random uuid
    """
    req_id = str(uuid.uuid4()).replace("-", "")

    logger = context_logger.bind(req_id=f"X-{req_id}")

    return logger

def verify_token(token: Annotated[str, Depends(oauth2_url)]) -> AuthenticationLevel:

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

    if username == "root":
        return AuthenticationLevel.ROOT
    elif username == "admin":
        return AuthenticationLevel.ADMIN
    else:
        return AuthenticationLevel.GENERAL
    
def verify_root_prviliage(authentication_level: Annotated[AuthenticationLevel, Depends(verify_token)]):

    if authentication_level == AuthenticationLevel.ROOT:
        return

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Only allow root user",
                        headers={"WWW-Authenticate": "Bearer"})

def verify_admin_prviliage(authentication_level: Annotated[AuthenticationLevel, Depends(verify_token)]):

    if authentication_level == AuthenticationLevel.ROOT:
        return
    
    elif authentication_level == AuthenticationLevel.ADMIN:
        return
    
    # general user can not authentic
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Only allow root user",
                        headers={"WWW-Authenticate": "Bearer"})

def verify_all_prviliage(authentication_level: Annotated[AuthenticationLevel, Depends(verify_token)]):
    return