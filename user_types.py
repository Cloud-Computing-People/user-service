from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    email: str
    isAdmin: bool

class UserLogin(BaseModel):
    username: str