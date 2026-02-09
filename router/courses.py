from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import mysql.connector
import jwt
import datetime
from jinja2.nodes import If
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext


router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/courses", response_class=HTMLResponse)
async def courses(request: Request):
    return templates.TemplateResponse("courses.html", {"request": request})
@router.post("/courses", response_class=HTMLResponse)
async def courses(request: Request,Course_code:str=Form(...),Division:str=Form(...)):
    SECRET_KEY = "132"
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/Auth/login")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_email = payload.get("email")
        print("user_email",user_email)

    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح

