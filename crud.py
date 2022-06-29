from sqlalchemy.orm import Session
from sqlalchemy import desc
from hasher import hash_password
import models, schemas
import os


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).order_by(desc(models.Post.id)).offset(skip).limit(limit).all()

def get_post_by_id(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def get_games(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Game).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(username = user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def create_game(db: Session, game: schemas.GameCreate):
    db_game = models(**game.dict())
    db.add(db_game)
    db.commit()
    db.refresh()
    return db_game



def update_avatar(db: Session, username: str, avatar_name: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user.avatar_name != "default.png":
        os.remove(f"static//avatars//{user.avatar_name}")
    user.avatar_name = avatar_name
    db.commit()
    db.refresh(user)

def set_supervisor(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    user.is_supervisor = True
    db.commit()
    db.refresh(user)
