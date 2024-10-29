from pydantic import BaseModel, Field
from typing import Annotated, Any, Optional, Dict, List


class User(BaseModel):
    id: Annotated[int, Field(description="User ID", examples=[1])]
    username: Annotated[
        str, Field(description="Username", examples=["totally-not-darth-vader"])
    ]
    email: Annotated[
        str, Field(description="User email", examples=["darth_vader@empire.gov"])
    ]
    is_admin: Annotated[bool, Field(description="User admin status", examples=[False])]


class UserLogin(BaseModel):
    username: str


class ResponseModel(BaseModel):
    data: Any
<<<<<<< HEAD
    links: Optional[List[Dict[str, str]]] = None
=======
    links: Optional[Dict[str, Optional[str]]] = None
>>>>>>> af7466e (fix links x2)
