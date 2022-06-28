import hasher
from sqlalchemy.orm import Session
from crud import get_user
from fastapi import Depends
from database import get_db
from fastapi import HTTPException, status
from utils import OAuth2PasswordBearerWithCookie
from jose import jwt, JWTError
from config import settings


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = get_user(username=username, db=db)
    print(user)
    if not user:
        return False
    if not hasher.verify_password(password, user.hashed_password):
        return False
    return user

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        print("username extracted is ", username)
        if username is None:
            raise credentials_exception
    except JWTError:
        print("JWTError")
        raise credentials_exception
    user = get_user(username=username, db=db)
    if user is None:
        raise credentials_exception
    return user