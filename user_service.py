import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Query, Path
from pydantic import BaseModel
import pymysql
from user_types import *
from sql_queries import *
from typing import Annotated

load_dotenv()

title = "User Service"
description = """
The user service manages all user-related activities, including:
login and authorization, checking game and marketplace access, and
reading and updating user attributes (username, profile picture, bio,
admin status, etc.). 

Functionality includes the ability to:
* Get attributes for all existing users.
* Get attributes for a specific user by user ID.
* Update attributes for a specific user by user ID.
* Create a new user.
"""
version = "0.0.1"

app = FastAPI(
    title=title,
    description=description,
    version=version
)
connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="userdb",
)
cursor = connection.cursor(pymysql.cursors.DictCursor)


@app.get("/users/{userId}")
async def getUser(
        userId: Annotated[
            int,
            Path(description="ID of the user to retrieve.")
        ]
    ):
    """
    Retrieve user info by user ID.
    """

    sql = getUserByIdSQL(userId)
    cursor.execute(sql)
    ret = [row for row in cursor]
    if len(ret) != 1:
        raise HTTPException(status_code=404, detail="User not found")
    return ret


@app.get("/users")
async def getUsers():
    """
    Retrieve data for all users.
    """

    sql = getUsersSQL()
    cursor.execute(sql)
    ret = [row for row in cursor]
    return ret


@app.post("/users")
async def createUser(
        user: Annotated[
            User,
            Query(description="")
        ]
    ):
    """
    Creates a new user.
    """

    sql = createUserSQL(user.id, user.username, user.email, user.isAdmin)
    print(sql)
    try:
        cursor.execute(sql)
    except:
        raise HTTPException(status_code=500)
    return user


@app.put("/users/{userId}")
async def updateUser(
        userId: Annotated[
            int,
            Path(description="ID of the user to update.")
        ],
        user: Annotated[
            User,
            Query(description="")
        ]
    ):
    """
    Updates information for an existing user.
    """

    sql = updateUserSQL(userId, user)
    try:
        cursor.execute(sql)
    except:
        raise HTTPException(status_code=500)
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
