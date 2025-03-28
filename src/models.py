from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    email: str
    name: str
    password: str
    team_id: int
    contact: str
    refresh_token: Optional[str] = None

class LoginModel(BaseModel):
    email: str
    password: str

class LogoutRequest(BaseModel):
    user_id: int