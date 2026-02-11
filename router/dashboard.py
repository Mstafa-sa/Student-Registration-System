from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import mysql.connector
import jwt
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os


load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")


router = APIRouter()
SECRET_KEY="132"
templates = Jinja2Templates(directory="templates")
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/Auth/login")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_email = payload.get("email")
        con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
        cursor = con.cursor()
        sql = "SELECT * FROM user WHERE email = %s"
        cursor.execute(sql,(user_email,))
        id = cursor.fetchone()
        sql = "SELECT count(*) FROM courses WHERE id_student = %s"
        cursor.execute(sql,(id[0],))
        numbers = cursor.fetchone()
        sql = "SELECT sum(الساعات) FROM courses WHERE id_student = %s"
        cursor.execute(sql, (id[0],))
        numberstime = cursor.fetchone()
        con.close()

        response = templates.TemplateResponse(
            "dashboard.html",
            {"request": request,"numbers":numbers,"numberstime":numberstime}
        )

        # 🔥 منع الكاش
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response

    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح
