import jwt
import datetime 
from typing import Optional
from passlib.context import CryptContext
from enum import Enum

from fastapi.security import OAuth2PasswordBearer

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_url = OAuth2PasswordBearer(tokenUrl="/v1/login/access-token")

class UnauthorizedError(BaseException):
    pass

class AuthenticationLevel(Enum):

    ROOT = "root"
    ADMIN = "admin"
    GENERAL = "general"


def generate_hashed_password(password: str) -> str:
    return pwd_context.hash(password)
    
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def generate_access_token(user_id: str, expires_delta: Optional[datetime.timedelta] = None) -> str:

    now = datetime.datetime.now(datetime.timezone.utc)

    expire = now + expires_delta if expires_delta is not None else now + datetime.timedelta(minutes=60 * 24)

    encoded_jwt = jwt.encode({"sub": user_id, "exp": expire},
                             SECRET_KEY,
                             algorithm=ALGORITHM)

    return encoded_jwt

def decode_token(token: str) -> dict:

    try:
        payload = jwt.decode(token,
                             SECRET_KEY,
                             algorithms=ALGORITHM)
        return payload
    except Exception as err:
        raise UnauthorizedError(f"{str(err)}")
