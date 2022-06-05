from datetime import datetime
from fastapi import FastAPI, Depends, Form, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import insert_post, get_post,insert_user, search_user

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="templates")

def makeDictOfPost():
    posts = get_post()
    return posts

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    posts = makeDictOfPost()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

# @app.route("/login", methods=["GET", "POST"])
@app.get("/registration", response_class=HTMLResponse)
def registration(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/registration")
def registration(username: str = Form(None, max_length=16), password: str = Form(None, max_length=16)):
    if username and password and not search_user((username,)):
        insert_user((username, password))
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/registration",status_code=303)
    

        
@app.get("/post", response_class=HTMLResponse)
def post(request: Request):
    return templates.TemplateResponse("postCreation.html", {"request": request})

@app.post("/post") #TODO post User_id
def post(title: str = Form(None, max_length=60), tenor: str = Form(None, max_length=300)):
    if title and tenor: #TODO check tITlE
        insert_post((1,datetime.now(),title,tenor))
        return RedirectResponse(url="/", status_code=303)
    return RedirectResponse(url="/post",status_code=303)

@app.get("/login")
def login():    
    pass
