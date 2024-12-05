from pydantic import BaseModel, Field
from typing import Annotated, Any, Optional, Dict, List
from datetime import datetime


class User(BaseModel):
    id: Annotated[int, Field(description="User ID", examples=[1])]
    username: Annotated[
        str, Field(description="Username", examples=["totally-not-darth-vader"])
    ]
    email: Annotated[
        str, Field(description="User email", examples=["darth_vader@empire.gov"])
    ]
    isAdmin: Annotated[bool, Field(description="User admin status", examples=[False])]

class UserCreate(BaseModel):
    username: Annotated[
        str, Field(description="Username", examples=["totally-not-darth-vader"])
    ]
    email: Annotated[
        str, Field(description="User email", examples=["darth_vader@empire.gov"])
    ]
    isAdmin: Annotated[bool, Field(description="User admin status", examples=[False])]


class UserLogin(BaseModel):
    username: str


class ResponseModel(BaseModel):
    data: Any
    links: Optional[Dict[str, Optional[str]]] = None


class UpdateEvent(BaseModel):
    event_type: str = Field(..., description="The type of update")
    entity: str = Field("user", description="The entity type associated with the event (user).")
    timestamp: datetime = Field(default_factory=datetime.now, description="The timestamp when the event was generated.")
    entity_id: int = Field(..., description="Unique identifier for the entiyy")
    data: dict = Field(..., description="A dictionary containing the updated fields and their new values or new values")
    request_id: str = Field(..., description="The request ID associated with the update for traceability across services")
