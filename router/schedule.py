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
    con=mysql.connector.connect(host="localhost",user="root",password="Admin@123",database="school")
    cur=con.cursor()
    cur.execute("select * from courses")
    courses=cur.fetchall()
    print("courses=",courses)
    return templates.TemplateResponse("schedule.html", {"request": request, "courses":courses})
