from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import jwt
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
import mysql.connector
from passlib.context import CryptContext

load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/manage_students", response_class=HTMLResponse)
async def index(request: Request):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
    cursor = con.cursor()
    sql = "select * from user where role = %s"
    cursor.execute(sql,("student",))
    students = cursor.fetchall()
    cursor.close()

    return templates.TemplateResponse("manage_students.html", {"request": request, "students": students})
@router.post("/manage_students", response_class=HTMLResponse)
async def manage_students(request: Request,name: str = Form(None), email: str = Form(None), Specialization: str = Form(None),password: str = Form(None),hid: str = Form(None),method: str = Form(...),check_password: str = Form(...)):
    if method == "post":
      con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="school"
        )
      cursor = con.cursor()
      sql = "insert into user (full_name,email,password,Specialization,role) values(%s,%s,%s,%s,%s)"
      if password==check_password:
          pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
          hash = pwd_context.hash(password)
          cursor.execute(sql,(name,email,hash,Specialization,hid))
          con.commit()
          con.close()
          return RedirectResponse("/ADM/manage_students",status_code=303)