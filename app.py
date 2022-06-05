from fastapi import FastAPI, Depends, Form, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import insert_post, insert_user, search_user

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    form = Request.form
    return templates.TemplateResponse("index.html", {"request": request})

# @app.route("/login", methods=["GET", "POST"])
@app.get("/registration", response_class=HTMLResponse)
def registration(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

# @app.post("/registration/")
# def registration(username: str = Form(), password: str = Form()):
#     user = search_user(username)


@app.post("/registration")
async def registration(request: Request):
    data = await request.form()
    username = data.get("username")
    
    if not search_user((username,)):
        insert_user((username, data.get("password")))
    

@app.get("/login")
def login():
    pass

@app.get("/items/")
def read_item(token: str = Depends(oauth2_scheme)):
    return {"token": token}