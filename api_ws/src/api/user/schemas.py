from pydantic import BaseModel

from typing import List

class UserInfoResp(BaseModel):
    user_id: str
    user_name: str
    user_role: str
    registered_at: str

class UsersInfoResp(BaseModel):
    users: List[UserInfoResp]

class RegisterUserReq(BaseModel):
    user_name: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    user_name: str