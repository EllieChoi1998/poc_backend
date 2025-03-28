from pydantic import BaseModel

class User(BaseModel):
    email: str
    name: str
    password: str
    team_id: int
    contact: str
