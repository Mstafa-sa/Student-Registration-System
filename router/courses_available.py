from fastapi import APIRouter, Request, Depends, Cookie, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import jwt
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

from blacklist import BLACKLIST
from db import get_connection
load_dotenv()  # ← تقرأ ملف .env

secret_key = os.getenv("JWT_SECRET")


router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/coursesAvailable", response_class=HTMLResponse)
async def courses_available(request: Request,token:str =Cookie(None)):

    if not token:
        return RedirectResponse(url="/Auth/login")
    if token in BLACKLIST:
        raise HTTPException(status_code=401)
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        major = payload.get("Specialization")
        print(major)
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = """
             SELECT s.subject_name, \
                    s.major_code, \
                    s.hours, \
                    s.subject_code, \
                    sec.room_code, \
                    sec.id, \
                    sec.teacher_name, \
                    sec.from_time, \
                    sec.todays,
                    sec.to_time
                   FROM sections sec
                   JOIN subject s ON sec.subject_id = s.id
                   WHERE major_code=%s\
                    """
        cursor.execute(sql,(major,))
        courses = cursor.fetchall()
        cursor.close()
        response = templates.TemplateResponse(
                   "coursesAvailable.html",
                   {"request": request,"courses":courses}
                       )

        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح
