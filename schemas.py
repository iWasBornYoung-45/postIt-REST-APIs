import pydantic
from enum import Enum
from datetime import datetime
from uuid import UUID
from typing import Annotated
from pydantic.types import StringConstraints
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status
from pydantic import ConfigDict

class PostFlag(str, Enum):
    TECH = 'tech'
    SOCIAL = 'soc'
    HEALTH = 'heal'

class BodySchema(pydantic.BaseModel):
    title: Annotated[str, StringConstraints(max_length=100)]
    content: Annotated[str, StringConstraints(max_length=1000)]
    content_type: PostFlag | None = PostFlag.TECH
    published: bool = True

class UserBodySchema(pydantic.BaseModel):
    email: pydantic.EmailStr
    phone: Annotated[int, pydantic.Field(strict=True, lt=10000000000, gt=1111111111)]
    password: Annotated[str, StringConstraints(min_length=8)]

class UserResponseSchema(UserBodySchema):
    password: str = pydantic.Field(exclude=True)
    user_id: int
    registered_at: datetime

class ResponseBody(BodySchema):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    added_on: datetime
    op: UserResponseSchema
    
class ResponseBody1(pydantic.BaseModel):
    post: ResponseBody
    upvotes: int

class PasswordChangeBody(UserBodySchema):
    email: pydantic.EmailStr | None = None
    phone: Annotated[int, pydantic.Field(strict=True, lt=10000000000, gt=1111111111)] | None = None

class AuthUsername(pydantic.BaseModel):
    username: pydantic.EmailStr | Annotated[int, pydantic.Field(lt=10000000000, gt=1111111111)]

class VoteSchema(pydantic.BaseModel):
    post_id: UUID
    vote: bool
    
def login_cred(form_payload: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        form_payload.username = AuthUsername(username=form_payload.username).username    
    except pydantic.ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.json())
    return form_payload
