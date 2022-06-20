from fastapi import FastAPI, Depends, Form, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from jose import jwt

from passlib.context import CryptContext

from sqlalchemy.orm import Session

from sql_db import crud, models, schemas
from sql_db.database import SessionLocal, engine



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="templates")



#TODO make hashier file


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return pwd_context.hash(password)



def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

#TODO merge with login
def authenticate_user(db: Session = Depends(get_db), username: str | None = None, password: str | None = None):
    """"Validation user login"""
    if username == None or password == None:
        return False
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """"Create token for session"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """if user active return User"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/registration")
def registration(request: Request):
    return templates.TemplateResponse("registration.html" ,{"request": request})


@app.post("/registration")
async def registration(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    errors = list()
    if not len(username):
        errors.append("Input username")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})
    db_user = crud.get_user_by_username(db=db, username = username)
    if db_user:
        errors.append("Username already registered")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})
    elif len(password) < 6:
        errors.append("To short password: requires 6 symbols or more")
        return templates.TemplateResponse("registration.html", {"request": request, "errors": errors})
    user = schemas.UserCreate(username=username, password=password)
    crud.create_user(db=db, user=user)
    return RedirectResponse("/", status_code=303)
    


@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html" ,{"request": request})


@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    errors = list()
    if not username:
        errors.append("WTF man? Don't touch html code!!!!")
        return templates.TemplateResponse("login.html" ,{"request": request, "errors": errors})
    elif not password:
        errors.append("WTF man? Don't touch html code!!!!")
        return templates.TemplateResponse("login.html" ,{"request": request, "errors": errors})
    user = crud.get_user_by_username(db=db, username=username)
    if not user:
        errors.append("I don't now this maggot")
        return templates.TemplateResponse("login.html" ,{"request": request, "errors": errors})
    else:
        if pwd_context.verify(password, user.hashed_password):
            
            return RedirectResponse("/", status_code=303)
    






@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# @app.post("/users/{user_id}/posts/", response_model=schemas.Post)
# def create_post_for_user(user_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
#     return crud.create_user_post(db=db, post=post, user_id=user_id)


# @app.post("/posts/", response_model=HTMLResponse)
# def create_post_for_user(user_id: int, title: str = Form(max_length=60), description: str= Form(max_length=300), db: Session = Depends(get_db)):
#     crud.create_user_post(db=db, post=post, user_id=user_id)
#     return


# @app.get("/posts/", response_model=list[schemas.Post])
# def read_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
#     posts = crud.get_posts(db, skip=skip, limit=limit)
#     return posts


def read_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts

#--------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    posts = read_posts(db=db)
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


@app.get("/news", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    posts = read_posts(db=db)
    return templates.TemplateResponse("news.html", {"request": request, "posts": posts})


# @app.route("/login", methods=["GET", "POST"])
@app.get("/registration", response_class=HTMLResponse)
def registration(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


# @app.post("/registration")
# def registration(username: str = Form(None, max_length=16), password: str = Form(None, max_length=16)):
#     if username and password and not search_user((username,)):
#         insert_user((username, password))
#         return RedirectResponse(url="/", status_code=303)
#     return RedirectResponse(url="/registration",status_code=303)
    
        
@app.get("/post", response_class=HTMLResponse)
def post(request: Request):
    return templates.TemplateResponse("postCreation.html", {"request": request})


@app.post("/post") #TODO post User_id
async def post(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    title = form.get("title")
    description = form.get("description")
    if title and description: #TODO check tITlE
        post = schemas.PostCreate(title=title, description=description)
        crud.create_user_post(db=db, post=post, user_id=1)
        return RedirectResponse(url="/news", status_code=303)
    return RedirectResponse(url="/post",status_code=303)
