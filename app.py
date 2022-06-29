from datetime import timedelta
import secrets as _secrets
from typing import Union
from urllib import response
from PIL import Image

from fastapi import FastAPI, Request, Response, Depends, Cookie, HTTPException, status, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, UJSONResponse
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
import crud

import schemas
import models
import time


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")



@app.get("/", response_class=HTMLResponse,)
def index(request: Request, db: Session = Depends(get_db)):
    posts = crud.get_posts(db=db)
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
async def registration(request: Request, db: Session = Depends(get_db), username: str = Form(None),password: str = Form(None)):
    errors = list()
    if username is None or password is None:
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})
    if not len(username):
        errors.append("Input username")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})
    db_user = crud.get_user(db=db, username=username)

    if db_user:
        errors.append("Username already registered")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})
    elif len(password) < 4:
        errors.append("To short password: requires 4 symbols or more")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})

    user = schemas.UserCreate(username=username, password=password)
    crud.create_user(db=db, user=user)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=302)
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
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie("access_token")
        return response
    else:
        return RedirectResponse(url="/", status_code=302)

    


@app.post("/login", response_model=schemas.Token)
def login_for_access_token(response: Response, request: Request,
    username: str = Form(None),password: str = Form(None),
    db: Session = Depends(get_db)):  #added response as a function parameter
    
    if username is None or password is None:
        return templates.TemplateResponse("login.html", {"request": request, "log": True})  
    user = authenticate_user(username, password, db)
    posts = crud.get_posts(db=db)
    
    errors = list()
    if not user:
        errors.append("Incorrect username or password")
        return templates.TemplateResponse("registration.html", {"request": request, "errors":errors, "log": True})    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    msg="Ok"
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)  #set HttpOnly cookie in response
    
    return response


@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie("access_token")
        return response
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

@app.post("/set_supervisor")
def set_supervisor(request: Request, db: Session = Depends(get_db), superpassword: str = Form(None)):
    if superpassword is None:
        response = RedirectResponse(url="/", status_code=302)

    token = request.cookies.get("access_token")
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        response = RedirectResponse(url="/", status_code=302)
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie("access_token")
        return response
    
    if  superpassword == settings.SUPERPASSWORD:
        crud.set_supervisor(db=db, username=current_user.username)
        return RedirectResponse("/", status_code=302)
    return RedirectResponse("/", status_code=302)

    

@app.post("/profile/upload_avatar")
async def upload_avatar(request: Request, avatar: Union[UploadFile, None] = File(None), db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if avatar is None:
        return RedirectResponse(url="/profile", status_code=302)

    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie("access_token")
        return response

    FILEPATH = "./static/avatars/"
    filename = avatar.filename
    extension = filename.split(".")[1]
    if extension not in ["jpg", "png"]:
        return RedirectResponse(url="/profile", status_code=302)
    token_name = _secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH + token_name
    file_content = await avatar.read()

    with open(generated_name, "wb") as f:
        f.write(file_content)
    img = Image.open(generated_name)
    w, h = img.size
    if( w < 300 and h < 300):
        return RedirectResponse(url="/profile", status_code=302)
    if(w>h):
        area = (w/2-h/2, 0, w/2+h/2, h)
    else:
        area = (0, h/2-w/2, w, h/2+w/2)
    
    img = img.crop(area)    
    img = img.resize(size = (300, 300))
    img.save(generated_name)
    avatar.close()
    crud.update_avatar(db=db,username=current_user.username,avatar_name=token_name)
    return RedirectResponse(url="/profile",status_code=302)
    

        

@app.get("/post", response_class=HTMLResponse)
def post(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        return RedirectResponse(url="/",status_code=302)
    if current_user.is_supervisor:
        return templates.TemplateResponse("postCreation.html", {"request": request, "user": current_user})
    return RedirectResponse(url="/",status_code=302)

@app.get("/post/{id}")
def post_id(request: Request,id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post_by_id(db=db, post_id=id)
    return db_post.description



@app.post("/post") 
async def post(request: Request, db: Session = Depends(get_db), img: Union[UploadFile, None] = File(None)):
    token = request.cookies.get("access_token")
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        return RedirectResponse(url="/",status_code=302)

    if current_user is None:
        errors = list()
        errors.append("Expired session. Please login.")
        return templates.TemplateResponse("login.html", {"request": request, "errors":errors})
    form = await request.form()
    title = form.get("title")
    description = form.get("description")

    FILEPATH = "./static/imgs/"
    filename = img.filename
    extension = filename.split(".")[1]
    if extension not in ["jpg", "png"]:
        return RedirectResponse(url="/post", status_code=302)
    token_name = _secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH + token_name
    file_content = await img.read()

    with open(generated_name, "wb") as f:
        f.write(file_content)
    img = Image.open(generated_name)
    w, h = img.size
    if( w < 160 and h < 160):
        return RedirectResponse(url="/post", status_code=302)
    if(w>h):
        area = (w/2-h/2, 0, w/2+h/2, h)
    else:
        area = (0, h/2-w/2, w, h/2+w/2)
    
    img = img.crop(area)    
    img = img.resize(size = (160, 160))
    img.save(generated_name)
    img.close()
    if title and description and current_user.is_supervisor:
        if len(description) > 300:
            short_description = description[:300] + "..."
            post = schemas.PostCreate(title=title,short_description=short_description,description=description, img_name=token_name)
        else:
            post = schemas.PostCreate(title=title,short_description=description,description=description, img_name=token_name)
            
        crud.create_user_post(db=db, post=post, user_id=current_user.id)
        return RedirectResponse(url="/", status_code=302)
    return RedirectResponse(url="/",status_code=302)

@app.get("/games", response_class=HTMLResponse)
def games(request: Request, db: Session = Depends(get_db)):
    games = crud.get_games(db=db)
    token = request.cookies.get("access_token")
    if token is None:
        return templates.TemplateResponse("games.html", {"request": request, "games": games})
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        return templates.TemplateResponse("games.html", {"request": request, "games": games})
    return templates.TemplateResponse("games.html", {"request": request, "games": games, "user": current_user})

@app.get("/game_post", response_class=HTMLResponse)
def game_post(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        return RedirectResponse(url="/games",status_code=302)
    if current_user.is_supervisor:
        return templates.TemplateResponse("game_post.html", {"request": request, "user": current_user})
    return RedirectResponse(url="/games",status_code=302)



@app.post("/game_post")
async def game_post(request: Request, db: Session = Depends(get_db),img: Union[UploadFile, None] = File(None)):
    token = request.cookies.get("access_token")
    try:
        scheme, param = get_authorization_scheme_param(token)
        current_user: models.User = get_current_user_from_token(token=param, db=db)
    except:
        return RedirectResponse(url="/",status_code=302)
    form = await request.form()
    title = form.get("title")
    description = form.get("description")
    requirements = form.get("requirements")
    FILEPATH = "./static/imgs/"
    filename = img.filename
    extension = filename.split(".")[1]
    if extension not in ["jpg", "png"]:
        return RedirectResponse(url="/game_post", status_code=302)
    token_name = _secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH + token_name
    file_content = await img.read()

    with open(generated_name, "wb") as f:
        f.write(file_content)
    img = Image.open(generated_name)
    w, h = img.size
    if( w < 160 and h < 160):
        return RedirectResponse(url="/game_post", status_code=302)
    if(w>h):
        area = (w/2-h/2, 0, w/2+h/2, h)
    else:
        area = (0, h/2-w/2, w, h/2+w/2)
    
    img = img.crop(area)    
    img = img.resize(size = (160, 160))
    img.save(generated_name)
    img.close()
    if title and description and current_user.is_supervisor:
        game = schemas.GameCreate(game_name=title, description=description,system_requirements=requirements, img_name=token_name)
        crud.create_game(db=db, game=game)
        return RedirectResponse(url="/", status_code=302)
    return RedirectResponse(url="/",status_code=302)
