import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from jose import jwt
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from db import  get_db,db_cursor
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
async def register(request: Request, email: str=Form(...), password: str=Form(...),db=Depends(get_db)):
    with db_cursor(db) as cursor:
      sql = "SELECT * FROM user WHERE email = %s "
      cursor.execute(sql, (email, ))
      user = cursor.fetchone()
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    if user and pwd_context.verify(password, user[3]):
        role = user[5]
        print(role)
        payload = {
            "email": user[2],
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }
        # إذا بدك تضيف specialization للطالب فقط
        if role == "student":
            payload["Specialization"] = user[4]
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        # تحديد صفحة التحويل حسب الدور
        if role == "student":
            redirect_url = "/STU/dashboard"
        elif role == "Admin":
            redirect_url = "/ADM/Admin_Dashboard"
        else:
            raise HTTPException(status_code=403, detail="Invalid role")

        response = RedirectResponse(url=redirect_url, status_code=303)

        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            path="/",
            samesite="Lax"
        )

        return response

    return templates.TemplateResponse("login.html", {"request": request ,"message":"Incorrect username or password"})
@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})
@router.post("/signup", response_class=HTMLResponse)
async def signup(request: Request,name: str=Form(...),email: str=Form(...),password: str=Form(...),
                 check_password:str=Form(...),Specialization:str=Form(...),hid:str=Form(...),db=Depends(get_db)):
    with db_cursor(db) as cursor:
      sql = "SELECT id FROM user WHERE email = %s "
      cursor.execute(sql, (email,))
      id_student=cursor.fetchone()
    if id_student==None:
      if password == check_password:
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        hash=pwd_context.hash(password)
        payload = {
            "email":email,
            "Specialization": Specialization,
            "exp": datetime.utcnow() + timedelta(hours=2)
        }
        token=jwt.encode(payload,secret_key,algorithm="HS256")
        with db_cursor(db) as cursor:
          sql = "insert into user (full_name,email,password,Specialization,role) values (%s,%s,%s,%s,%s)"
          cursor.execute(sql,(name,email,hash,Specialization,hid))
        response=RedirectResponse("/STU/dashboard", status_code=303)
        response.set_cookie(key="token", value=token, httponly=True)
        return response
      return templates.TemplateResponse("signup.html", {"request": request,"message":"Incorrect  password"})
    return templates.TemplateResponse("signup.html", {"request": request, "message": "Email is available"})
@router.get("/forgotPassword", response_class=HTMLResponse)
async def forgotPassword(request: Request):
    return templates.TemplateResponse("forgotPassword.html", {"request": request})
@router.post("/forgot-password", response_class=HTMLResponse)
async def forgot_password_submit(request: Request, email: str = Form(...),db=Depends(get_db)):
    # 1️ تحقق من وجود المستخدم
    with db_cursor(db) as cursor:
      cursor.execute("SELECT id FROM user WHERE email=%s", (email,))
      user = cursor.fetchone()
    if not user:
        return templates.TemplateResponse(
            "forgotPassword.html",
            {"request": request, "message": "لا يوجد مستخدم بهذا البريد"}
        )
    user_id = user[0]
    # 2️ توليد توكن فريد
    reset_token = secrets.token_urlsafe(32)
    # 3⃣ حدد مدة انتهاء صلاحية التوكن (مثلاً 1 ساعة)
    expires_at = datetime.utcnow() + timedelta(hours=3,minutes=15)
    # 4️ احفظ التوكن في قاعدة البيانات
    with db_cursor(db) as cursor:
      cursor.execute(
        "INSERT INTO reset_password_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
        (user_id, reset_token, expires_at)
      )
    # 5️ إنشاء الرابط
    BASE_URL = "http://127.0.0.1:8001"  # استخدم HTTPS في production
    reset_link = f"{BASE_URL}/Auth/resetPassword/{reset_token}"
    # 6️ أرسل الرابط عبر البريد
    await send_email(email, reset_link)
    return templates.TemplateResponse(
        "forgotPassword.html",
        {"request": request, "message": "تم إرسال رابط إعادة التعيين إلى بريدك الإلكتروني"}
    )
@router.get("/resetPassword/{token}", response_class=HTMLResponse)
async def reset_password_form(request: Request, token: str,db=Depends(get_db)):
    with db_cursor(db) as cursor:
      sql= """
        SELECT * FROM reset_password_tokens
        WHERE token = %s
        AND used = 0 AND expires_at > NOW()
        """
      cursor.execute(sql, (token,))
      token_entry = cursor.fetchone()
    if not token_entry:
        return HTMLResponse(content="رابط إعادة التعيين غير صالح أو منتهي", status_code=400)
    # لا تعرض الإيميل مباشرة في الصفحة
    return templates.TemplateResponse(
        "reset-password.html",
        {"request": request, "token": token, "message": ""}
    )
@router.post("/resetPassword/{token}", response_class=HTMLResponse)
async def reset_password_submit(request: Request, token: str, new_password: str = Form(...),db=Depends(get_db)):
    with db_cursor(db) as cursor:
    # تحقق من صحة التوكن
      sql = """
          SELECT id, user_id \
          FROM reset_password_tokens
          WHERE token = %s \
            AND used = 0 \
            and expires_at > NOW() \
          """
      cursor.execute(sql, (token,))
      token_entry = cursor.fetchone()
    if not token_entry:
        return HTMLResponse(content="رابط إعادة التعيين غير صالح أو منتهي", status_code=400)
    with db_cursor(db) as cursor:
      sql="select email from user where id = %s"
      cursor.execute(sql, (token_entry["user_id"],))
      user = cursor.fetchone()
    if not user:
        return HTMLResponse(content="رابط إعادة التعيين غير صالح أو منتهي", status_code=400)
    # تحديث كلمة السر في قاعدة البيانات
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    hash = pwd_context.hash(new_password)
    with db_cursor(db) as cursor:
      cursor.execute("UPDATE user SET password=%s WHERE email=%s", (hash, user[0]))
    with db_cursor(db) as cursor:
    # تعليم التوكن بأنه مستعمل
      cursor.execute("UPDATE reset_password_tokens SET used=1 WHERE id=%s", (token_entry['id'],))
    return templates.TemplateResponse("reset-password.html",
                                      {"request": request, "message": "تم تغيير كلمة السر بنجاح!"})

