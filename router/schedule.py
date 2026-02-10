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

import mysql.connector
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/schedule", response_class=HTMLResponse)
async def index(request: Request):
    SECRET_KEY = "132"
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/Auth/login")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_email = payload.get("email")
        con=mysql.connector.connect(host="localhost",user="root",password="Admin@123",database="school")
        cursor = con.cursor()
        sql="select id from user where email=%s"
        cursor.execute(sql,(user_email,))
        id=cursor.fetchone()
        sql="select * from courses where id_student=%s"
        cursor.execute(sql,(id[0],))
        courses=cursor.fetchall()




        return templates.TemplateResponse("schedule.html", {"request": request, "courses":courses})
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح

