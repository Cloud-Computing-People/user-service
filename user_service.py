import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Query, Path, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pymysql
from pymysql import MySQLError
from models import *
from sql_queries import *
from typing import Annotated, List
from utils import *
from middleware import OverallMiddleware, http_exception_handler, generic_exception_handler
from pub_utils import publish_event


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

tags_metadata = [{"name": "Users", "description": "Basic operations on users."}]

app = FastAPI(
    title=title, description=description, version=version, openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.add_middleware(OverallMiddleware)


connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database="userdb",
)
cursor = connection.cursor(pymysql.cursors.DictCursor)


@app.get(
    "/users/{user_id}", response_model=ResponseModel, status_code=status.HTTP_200_OK,
    tags=["Users"]
)
async def get_user(
    user_id: Annotated[int, Path(description="User ID of user to retrieve")],
    include_player_data: Optional[bool] = False,
):
    """
    Retrieve user info by user ID.
    """

    sql = get_user_by_id_sql(user_id)
    if include_player_data:
        sql = get_user_player_by_id_sql(user_id)

    try:
        cursor.execute(sql)
        ret = cursor.fetchone()
        if not ret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        
        links = {
            "self": f"/users/{user_id}",
            "all_users": "/users",
            "update": f"/users/{user_id}"
        }
        response = format_response(data=ret, links=links)
        return response

    except MySQLError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@app.get(
    "/users/email/{email}", response_model=ResponseModel, status_code=status.HTTP_200_OK,
    tags=["Users"]
)
async def get_user_by_email(
    email: Annotated[str, Path(description="Email ID of user to retrieve")],
    include_player_data: Optional[bool] = False,
):
    """
    Retrieve user info by email ID.
    """
    sql = get_user_by_email_sql(email)
    if include_player_data:
        sql = get_user_player_by_email_sql(email)

    try:
        cursor.execute(sql)
        ret = cursor.fetchone()
        if not ret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        
        links = {
            "self": f"/users/email/{email}",
            "all_users": "/users",
            "update": f"/users/{ret['id']}"
        }
        response = format_response(data=ret, links=links)
        return response

    except MySQLError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@app.get(
    "/users",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Users"],
)
async def get_users(limit: Optional[int] = 10, offset: Optional[int] = 0):
    sql = get_users_sql()
    sql += f" LIMIT {limit} OFFSET {offset};"

    try:
        cursor.execute(sql)
        ret = cursor.fetchall()
        links = {
            "self": f"/users?limit={limit}&offset={offset}",
            "next": f"/users?limit={limit}&offset={offset + limit}" if len(ret) == limit else None,
            "prev": f"/users?limit={limit}&offset={max(0, offset - limit)}" if offset > 0 else None
        }
        response = format_response(data=ret, links=links)
        return response

    except MySQLError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


@app.post(
    "/users",
    response_model=ResponseModel,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
async def create_user(user: UserCreate, request: Request):
    try:
        sql_check = get_user_by_email_sql(user.email)
        cursor.execute(sql_check)
        ret = cursor.fetchone()
        if ret:
            raise HTTPException(
                status_code=400, detail="User with email already exists."
            )
        
        sql = create_user_sql(user.username, user.email, user.isAdmin)
        cursor.execute(sql)
        if not user.isAdmin:
            cursor.execute(get_user_by_email_sql(user.email))
            ret = cursor.fetchone()
            sql = f"INSERT INTO PLAYER_DATA (id, profilePic, bio, totalCurrency, activeItem) VALUES ({ret['id']}, '', '', 0, NULL);"
            cursor.execute(sql)
        
        connection.commit()
        user = User(**user.model_dump(), id=ret["id"])
        links = {
            "self": f"/users/{user.id}",
            "update": f"/users/{user.id}"
        }
        response = format_response(data=dict(user), links=links)

        event = UpdateEvent(
            event_type="create",
            entity="user",
            entity_id=user.id,
            data={**dict(user), "PLAYER_DATA.id": user.id, 'bio': '', 'profilePic': '', 'activeItem': None, "totalCurrency": 0},
            request_id=request.state.request_id
        )
        
        if os.environ.get("PUBLISH_EVENTS") == "True":
            publish_event(event.model_dump())

        return response

    except MySQLError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


@app.put(
    "/users/{user_id}",
    response_model=ResponseModel,
    status_code=status.HTTP_200_OK,
    tags=["Users"],
)
async def update_user(
    user_id: Annotated[int, Path(description="User ID of user to update")], user: User,
    request: Request
):
    sql = update_user_sql(user_id, user) + ";"

    try:
        cursor.execute(sql)
        connection.commit()
        links = {"self": f"/users/{user.id}"}
        response = format_response(data=user, links=links)

        event = UpdateEvent(
            event_type="update",
            entity="user",
            entity_id=user_id,
            data=dict(user),
            request_id=request.state.request_id
        )
        
        if os.environ.get("PUBLISH_EVENTS") == "True":
            publish_event(event.model_dump())

        return response

    except MySQLError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))


@app.post(
    "/users/{user_id}/balance/add",
    response_model=ResponseModel,
    summary="Add balance to user's account",
)
async def add_balance(
    user_id: Annotated[
        int, Path(description="ID of the user whose balance will be updated.")
    ],
    amount: float,
    request: Request
):
    try:
        sql = get_user_player_by_id_sql(user_id)
        cursor.execute(sql)
        ret = cursor.fetchone()
        if not ret:
            raise HTTPException(status_code=404, detail="User not found.")

        sql = add_balance_sql(user_id, amount)
        cursor.execute(sql)
        connection.commit()

        links = {
            "self": f"/users/{user_id}/balance/add",
            "user": f"/users/{user_id}",
            "deduct_balance": f"/users/{user_id}/balance/deduct"
        }

        event = UpdateEvent(
            event_type="update",
            entity="user",
            entity_id=user_id,
            data={**ret, "totalCurrency": ret["totalCurrency"] + amount},
            request_id=request.state.request_id
        )
        
        if os.environ.get("PUBLISH_EVENTS") == "True":
            publish_event(event.model_dump())

        return ResponseModel(data={}, links=links)

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=" Balance update failed: " + str(e))


@app.post(
    "/users/{user_id}/balance/deduct",
    response_model=ResponseModel,
    summary="Deduct balance to user's account",
)
async def deduct_balance(
    user_id: Annotated[
        int, Path(description="ID of the user whose balance will be updated.")
    ],
    amount: float,
    request: Request
):
    try:
        sql = get_user_player_by_id_sql(user_id)
        cursor.execute(sql)
        ret = cursor.fetchone()
        if not ret:
            raise HTTPException(status_code=404, detail="User not found.")

        sql = get_balance_sql(user_id)
        cursor.execute(sql)
        c = cursor.fetchone()
        if c["totalCurrency"] < amount:
            raise HTTPException(
                status_code=400, detail="User does not have enough funds."
            )

        sql = deduct_balance_sql(user_id, amount)
        cursor.execute(sql)
        connection.commit()

        event = UpdateEvent(
            event_type="update",
            entity="user",
            entity_id=user_id,
            data={**ret, "totalCurrency": ret["totalCurrency"] - amount},
            request_id=request.state.request_id
        )       

        if os.environ.get("PUBLISH_EVENTS") == "True":
            publish_event(event.model_dump())

        links = {
            "self": f"/users/{user_id}/balance/deduct",
            "user": f"/users/{user_id}",
            "add_balance": f"/users/{user_id}/balance/add",
        }

        return ResponseModel(data={}, links=links)

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=" Balance update failed: " + str(e))


@app.get(
    "/users/{user_id}/balance",
    response_model=ResponseModel,
    summary="Retrieve user balance",
)
async def get_balance(
    user_id: int = Path(
        ..., description="ID of the user whose balance will be retrieved."
    ),
):
    try:
        sql = get_balance_sql(user_id)
        cursor.execute(sql)
        ret = cursor.fetchone()
        if not ret:
            raise HTTPException(status_code=404, detail="User not found.")

        links = {
            "self": f"/users/{user_id}/balance",
            "add_balance": f"/users/{user_id}/balance/add",
            "deduct_balance": f"/users/{user_id}/balance/deduct",
        }

        return ResponseModel(data={"totalCurrency": ret["totalCurrency"]}, links=links)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Unable to retrieve balance: " + str(e)
        )

@app.put(
    "/users/{user_id}/equip/{item_id}",
)
def equip_item(user_id: int, item_id: int, request: Request):
    try:
        sql = equip_item_sql(user_id, item_id)
        cursor.execute(sql)
        connection.commit()

        event = UpdateEvent(
            event_type="equip",
            entity="user",
            timestamp=datetime.now().isoformat(),
            entity_id=user_id,
            data={"activeItem": item_id},
            request_id=request.state.request_id
        )
        
        if os.environ.get("PUBLISH_EVENTS") == "True":
            publish_event(event.model_dump())

        return JSONResponse(status_code=200, content={"message": "Item equipped."})

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail="Item equip failed: " + str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
