from datetime import timedelta
import secrets as _secrets
from typing import Union

from fastapi import FastAPI, Request, Response, Depends, Cookie, HTTPException, status, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
from utils import OAuth2PasswordBearerWithCookie
from database import engine, get_db
from security import create_access_token
from auth import authenticate_user, get_current_user_from_token
from config import settings
from crud import create_user, get_user, create_user_post, get_posts
from forms import LoginForm

import schemas
import models
import time


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")



@app.get("/", response_class=HTMLResponse,)
def index(request: Request, db: Session = Depends(get_db)):
    posts = get_posts(db=db)
    token = request.cookies.get("access_token")
    if token is None:
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts})
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts})
    if current_user is None:
        return templates.TemplateResponse("index.html", {"request": request, "posts": posts})
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts, "user":current_user})
    


@app.get("/registration", response_class=HTMLResponse)
def registration(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/registration")
async def registration(request: Request, db: Session = Depends(get_db), username: str = Form(...),password: str = Form(...)):
    errors = list()
    if not len(username):
        errors.append("Input username")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})
    db_user = get_user(db=db, username=username)

    if db_user:
        errors.append("Username already registered")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})
    elif len(password) < 4:
        errors.append("To short password: requires 4 symbols or more")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})

    user = schemas.UserCreate(username=username, password=password)
    create_user(db=db, user=user)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}",
                        httponly=True)  # set HttpOnly cookie in response
    time.sleep(5)
    return response


@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/logout", response_class=RedirectResponse)
def logout(request: Request, response: Response):
    token = request.cookies.get("access_token")
    if token:
        response = RedirectResponse(url="/", status_code=303)
        response.delete_cookie("access_token")
        return response
    else:
        return RedirectResponse(url="/", status_code=303)

    


@app.post("/login", response_model=schemas.Token)
def login_for_access_token(response: Response, request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):  #added response as a function parameter
    user = authenticate_user(form_data.username, form_data.password, db)
    posts = get_posts(db=db)
    
    errors = list()
    if not user:
        errors.append("Incorrect username or password")
        return templates.TemplateResponse("login.html", {"request": request, "errors":errors})  
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    msg="Ok"
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)  #set HttpOnly cookie in response
    
    return response

    # return {"access_token": access_token, "token_type": "bearer"}

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        response = RedirectResponse(url="/", status_code=303)
        response.delete_cookie("access_token")
        return response
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

@app.post("/profile/change_avatar")
def change_avatar(request: Request, avatar: UploadFile = File(...), db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        response = RedirectResponse(url="/", status_code=303)
        response.delete_cookie("access_token")
        return response

    FILEPATH = "./static/"
    filename = avatar.filename
    extension = filename.split(".")[1]
    if extension not in ["jpg", "png"]:
        return RedirectResponse(url="/profile", status_code=407)
    token_name = _secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH + token_name
    

        

@app.get("/post", response_class=HTMLResponse)
def post(request: Request):
    return templates.TemplateResponse("postCreation.html", {"request": request})


@app.post("/post") #TODO post User_id
async def post(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    scheme, param = get_authorization_scheme_param(token)
    current_user: models.User = get_current_user_from_token(token=param, db=db)
    if current_user is None:
        errors = list()
        errors.append("Expired session. Please login.")
        return templates.TemplateResponse("login.html", {"request": request, "errors":errors})
    form = await request.form()
    title = form.get("title")
    description = form.get("description")
    if title and description and get_user(db=db,username=current_user.username): #TODO check tITlE
        post = schemas.PostCreate(title=title, description=description)
        create_user_post(db=db, post=post, user_id=current_user.id)
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/",status_code=303)

