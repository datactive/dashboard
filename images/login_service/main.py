import secrets
import os
# from bokeh.util import session_id
from bokeh.util.token import generate_session_id

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse, HTMLResponse

from fastapi.templating import Jinja2Templates


app = FastAPI()

security = HTTPBasic()
templates = Jinja2Templates(directory="templates")


DASHBOARD_URL = os.environ['LOGIN_DASHBOARD_URL']
USERNAME = os.environ['LOGIN_USERNAME']
PASS = os.environ['LOGIN_PASSWORD']

def auth_user(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = bytes(f'{USERNAME}', "utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = bytes(f'{PASS}', "utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/login", response_class=RedirectResponse, status_code=302)
def redirect_panel(username: str = Depends(auth_user)):
    s_id = generate_session_id()
    return f"{DASHBOARD_URL}?bokeh-session-id={s_id}"
