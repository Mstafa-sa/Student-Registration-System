from fastapi import APIRouter, Request, Cookie, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

from auth_utils import get_current_user
from blacklist import BLACKLIST
from db import get_connection
from passlib.context import CryptContext
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()
# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/manage_students", response_class=HTMLResponse)
async def index(request: Request,user: dict = Depends(get_current_user)):
    if user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")
    con = get_connection()
    cursor = con.cursor(buffered=True)
    sql = "select * from user where role = %s"
    cursor.execute(sql,("student",))
    students = cursor.fetchall()
    cursor.close()
    response = templates.TemplateResponse(
        "manage_students.html",
        {"request": request, "students": students}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response
@router.post("/manage_students", response_class=HTMLResponse)
async def manage_students(request: Request,name: str = Form(None), email: str = Form(None), Specialization: str = Form(None),password: str = Form(None),
                          hid: str = Form(None),check_password: str = Form(None),search: str = Form(None),student_id:int=Form(None),action: str = Form(...),user: dict = Depends(get_current_user)):
    if user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    if action == "add":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        cursor.execute("SELECT id FROM user WHERE email=%s ", (email,))
        student = cursor.fetchone()
        cursor.close()
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = "select * from user where role = %s"
        cursor.execute(sql, ("student",))
        students = cursor.fetchall()
        cursor.close()
        if student == None:
           con = get_connection()
           cursor = con.cursor()
           sql = "insert into user (full_name,email,password,Specialization,role) values(%s,%s,%s,%s,%s)"
           if password==check_password:
              pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
              hash = pwd_context.hash(password)
              cursor.execute(sql,(name,email,hash,Specialization,"student"))
              con.commit()
              con.close()
              return RedirectResponse("/ADM/manage_students",status_code=303)
        return templates.TemplateResponse("manage_students.html", {"request": request, "msege": "هذا البريد الإلكتروني موجود مسبقاً، لا يمكن استخدامه لطالب آخر!", "students": students})
    elif action == "serch":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = "select * from user where (full_name = %s or Specialization=%s or id=%s) and role=%s "
        cursor.execute(sql,(search,search,search,"student"))
        students = cursor.fetchall()
        cursor.close()
        return templates.TemplateResponse("manage_students.html", {"request": request, "students": students})
    elif action == "delete":
        con = get_connection()
        cursor = con.cursor()
        sql = "delete from user where id=%s"
        cursor.execute(sql,(student_id,))
        con.commit()
        con.close()
        return RedirectResponse("/ADM/manage_students",status_code=303)
    elif action == "edit":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        cursor.execute("SELECT id FROM user WHERE email=%s AND id != %s", (email, student_id))
        student = cursor.fetchone()
        cursor.close()
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = "select * from user where role = %s"
        cursor.execute(sql, ("student",))
        students = cursor.fetchall()
        cursor.close()
        if student == None:
          con = get_connection()
          cursor = con.cursor()
          # فقط حدث البيانات بدون كلمة السر
          sql = "UPDATE user SET full_name=%s, email=%s, Specialization=%s WHERE id=%s"
          cursor.execute(sql, (name, email, Specialization, student_id))
          con.commit()
          con.close()
          return RedirectResponse("/ADM/manage_students", status_code=303)
        return  templates.TemplateResponse("manage_students.html", {"request": request,"msege":"هذا البريد الإلكتروني موجود مسبقاً، لا يمكن استخدامه لطالب آخر!","students":students})


