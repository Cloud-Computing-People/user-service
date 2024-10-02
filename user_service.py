import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymysql
from user_types import *
from sql_queries import *

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="userdb",
)
cursor = connection.cursor(pymysql.cursors.DictCursor)


@app.get("/users/{userId}")
async def getUser(userId):
    sql = getUserByIdSQL(userId)
    cursor.execute(sql)
    ret = [row for row in cursor]
    if len(ret) != 1:
        raise HTTPException(status_code=404, detail="User not found")
    return ret


@app.get("/users")
async def getUsers():
    sql = getUsersSQL()
    cursor.execute(sql)
    ret = [row for row in cursor]
    return ret


@app.post("/users")
async def createUser(user: User):
    sql = createUserSQL(user.id, user.username, user.email, user.isAdmin)
    print(sql)
    try:
        cursor.execute(sql)
    except:
        raise HTTPException(status_code=500)
    return user


@app.put("/users/{userId}")
async def updateUser(userId: int, user: User):
    sql = updateUserSQL(userId, user)
    try:
        cursor.execute(sql)
    except:
        raise HTTPException(status_code=500)
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8002)
