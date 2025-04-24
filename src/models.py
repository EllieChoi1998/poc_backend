from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    login_id: str
    ibk_id: str
    name: str
    password: str
    hiearchy: str
    system_role: str
    team_id: Optional[int] = None
    activate: str = 'T'
    refresh_token: Optional[str] = None

class LoginModel(BaseModel):
    login_id: str
    password: str

class LogoutRequest(BaseModel):
    user_id: int