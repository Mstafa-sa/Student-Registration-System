from fastapi import APIRouter, Request, Cookie, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from blacklist import BLACKLIST
from db import get_connection
import jwt
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")

router = APIRouter()


# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/schedule", response_class=HTMLResponse)
async def index(request: Request,token:str =Cookie(None)):
    if not token:
        return RedirectResponse(url="/Auth/login")
    if token in BLACKLIST:
        raise HTTPException(status_code=401)
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_email = payload.get("email")
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql="select id from user where email=%s"
        cursor.execute(sql,(user_email,))
        id=cursor.fetchone()
        cursor.close()
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql="select * from courses where id_student=%s"
        cursor.execute(sql,(id[0],))
        courses=cursor.fetchall()
        cursor.close()
        response = templates.TemplateResponse(
            "schedule.html",
            {"request": request,"courses":courses }
        )
        # 🔥 منع الكاش
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح

