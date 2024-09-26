from fastapi import FastAPI, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    userID: int
    username: str
    isAdmin: bool

class UserLogin(BaseModel):
    username: str

# Mock user data
# @TODO: replace with database integration
users = {
    "user1": {"userID": 1, "username": "user1", "isAdmin": True},
    "user1": {"userID": 2, "username": "user2", "isAdmin": False}
}

class Settings(BaseModel):
    authjwt_secret_key: str = "TODO-change-key"

@AuthJWT.load_config
def get_config():
    return Settings()

@app.post('/login')
def login(user: UserLogin, Authorize: AuthJWT = Depends()):
    if user.username in users:
        access_token = Authorize.create_access_token(subject=user.username)
        return {"access_token": access_token}
    raise HTTPException(status_code=404, detail="User not found")

@app.get('/profile')
def profile(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user_data = users.get(current_user)
    if user_data:
        return user_data
    raise HTTPException(status_code=404, detail="User not found")

if __name__ == "__main__":
