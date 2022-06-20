from typing import List, Union

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class PostBase(BaseModel):
    title: str
    description: Union[str, None] = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    img_name: str
    owner_id: int

    class Config:
        orm_mode = True




class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    avatar_name: str
    is_active: bool
    posts: List[Post] = []

    class Config:
        orm_mode = True




class GameBase(BaseModel):
    title: str
    description: Union[str, None] = None
    system_requirements: Union[str, None] = None


class GameCreate(GameBase):
    pass


class Game(GameBase):
    id: int

    class Config:
        orm_mode = True
