from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import jwt
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()  # ← تقرأ ملف .env

secret_key = os.getenv("JWT_SECRET")


router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/coursesAvailable", response_class=HTMLResponse)
async def courses_available(request: Request):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/Auth/login")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        major = payload.get("Specialization")
        con = mysql.connector.connect(
          host="localhost",
           user="root",
           password=os.getenv("DB_PASSWORD"),
          database="school"
         )
        cursor = con.cursor()
        sql = """
             SELECT s.subject_name, \
                    s.major_code, \
                    s.الساعات, \
                    s.subject_code, \
                    sec.room_code, \
                    sec.id, \
                    sec.teacher_name, \
                    sec.time, \
                    sec.todays
                   FROM sections sec
                   JOIN subject s ON sec.subject_id = s.id
                   WHERE major_code=%s
                    """
        cursor.execute(sql,(major,))
        courses = cursor.fetchall()

        response = templates.TemplateResponse(
                   "coursesAvailable.html",
                   {"request": request,"courses":courses}
                       )


        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح
