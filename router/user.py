import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi import Form
import jwt
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from db import get_connection
from email_utils import send_email  # هنا نستدعي الدالة
load_dotenv()  # ← تقرأ ملف .env
otp_store = {}
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()
reset_tokens = {}
# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@router.post("/login", response_class=HTMLResponse)
async def register(request: Request, email: str=Form(...), password: str=Form(...)):

    con = get_connection()
    cursor = con.cursor(buffered=True)
    sql = "SELECT * FROM user WHERE email = %s "
    cursor.execute(sql, (email, ))
    user = cursor.fetchone()
    cursor.close()
    con.close()
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    if user and pwd_context.verify(password, user[3]):
        if user [5] == "student":
         payload = {
                "email": user[2],
                "Specialization": user[4],
                "exp": datetime.utcnow() + timedelta(hours=2)
            }

         Token = jwt.encode(payload, secret_key, algorithm="HS256")
         response = RedirectResponse(url="/STU/dashboard", status_code=303)
         response.set_cookie(key="token", value=Token, httponly=True)  # httponly لتحسين الأمان
         return response
        elif user [5] == "Admin":
            payload = {
                "email": user[2],
                "exp": datetime.utcnow() + timedelta(hours=2)
            }
            Token = jwt.encode(payload, secret_key, algorithm="HS256")
            response = RedirectResponse(url="/ADM/Admin_Dashboard", status_code=303)
            response.set_cookie(key="token_ad", value=Token, httponly=True)  # httponly لتحسين الأمان
            return response
        return templates.TemplateResponse("login.html", {"request": request,"message":"المستخدم غير موجود"})
    return templates.TemplateResponse("login.html", {"request": request ,"message":"Incorrect username or password"})
@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})
@router.post("/signup", response_class=HTMLResponse)
async def signup(request: Request,name: str=Form(...),email: str=Form(...),password: str=Form(...), check_password:str=Form(...),Specialization:str=Form(...),hid:str=Form(...)):
    con = get_connection()
    cursor = con.cursor()
    sql="insert into user (full_name,email,password,Specialization,role) values (%s,%s,%s,%s,%s)"
    if password == check_password:
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        hash=pwd_context.hash(password)
        payload = {
            "email":email,
            "Specialization": Specialization,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }
        token=jwt.encode(payload,secret_key,algorithm="HS256")
        cursor.execute(sql,(name,email,hash,Specialization,hid))
        con.commit()
        cursor.close()
        con.close()
        response=RedirectResponse("/STU/dashboard", status_code=303)
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    return templates.TemplateResponse("signup.html", {"request": request,"message":"Incorrect username or password"})
@router.get("/forgotPassword", response_class=HTMLResponse)
async def forgotPassword(request: Request):
    return templates.TemplateResponse("forgotPassword.html", {"request": request})


@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(request: Request, email: str = Form(...)):
    # ... التحقق من DB
    reset_token = secrets.token_urlsafe(16)
    reset_tokens[reset_token] = email
    BASE_URL = "http://127.0.0.1:8001"
    reset_link = f"{BASE_URL}/Auth/resetPassword/{reset_token}"

    print("Email:", email)
    print("Reset link:", reset_link)

    # استدعاء الدالة من الملف الخارجي
    await send_email(email, reset_link)

    return templates.TemplateResponse("forgotPassword.html", {"request": request, "message": "تم إرسال رابط إعادة التعيين"})



@router.get("/resetPassword/{token}", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str):
    email = reset_tokens.get(token)
    if not email:
        return HTMLResponse(content="رابط إعادة التعيين غير صالح أو منتهي", status_code=400)
    return templates.TemplateResponse("reset-password.html", {"request": request, "message": ""})

@router.post("/resetPassword/{token}", response_class=HTMLResponse)
async def reset_password_submit(request: Request, token: str, new_password: str = Form(...)):
    email = reset_tokens.get(token)
    if not email:
        return HTMLResponse(content="رابط إعادة التعيين غير صالح أو منتهي", status_code=400)

    # تحديث كلمة السر في قاعدة البيانات
    con = get_connection()
    cursor = con.cursor()
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    hash = pwd_context.hash(new_password)
    cursor.execute("UPDATE user SET password=%s WHERE email=%s", (hash, email))
    con.commit()
    cursor.close()
    con.close()

    # إزالة التوكن بعد الاستخدام
    del reset_tokens[token]

    return templates.TemplateResponse("reset_password.html", {"request": request, "message": "تم تغيير كلمة السر بنجاح!"})

