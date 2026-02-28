from fastapi import APIRouter, Request,  HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from auth_utils import get_current_user
from db import  get_db,db_cursor
from passlib.context import CryptContext
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()
# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/manage_students", response_class=HTMLResponse)
async def index(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    if user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")
    with db_cursor(db) as cursor:
        sql="select * from major  "
        cursor.execute(sql)
        majors = cursor.fetchall()
    with db_cursor(db) as cursor:
      sql = "select * from user where role = %s"
      cursor.execute(sql,("student",))
      students = cursor.fetchall()
    response = templates.TemplateResponse(
        "manage_students.html",
        {"request": request, "students": students,"majors": majors}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response
@router.post("/manage_students", response_class=HTMLResponse)
async def manage_students(request: Request,name: str = Form(None), email: str = Form(None), Specialization: str = Form(None),password: str = Form(None),
                          db=Depends(get_db),check_password: str = Form(None),search: str = Form(None),student_id:int=Form(None),action: str = Form(...),user: dict = Depends(get_current_user)):
    if user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")

    if action == "add":
        with db_cursor(db) as cursor:
          cursor.execute("SELECT id FROM user WHERE email=%s ", (email,))
          student = cursor.fetchone()
        with db_cursor(db) as cursor:
          sql = "select * from user where role = %s"
          cursor.execute(sql, ("student",))
          students = cursor.fetchall()
        if student != None:
            return templates.TemplateResponse("manage_students.html", {"request": request, "msege": "هذا البريد الإلكتروني موجود مسبقاً، لا يمكن استخدامه لطالب آخر!",   "students": students})
        if password==check_password:
          with db_cursor(db) as cursor:
            sql = "insert into user (full_name,email,password,Specialization,role) values(%s,%s,%s,%s,%s)"
            pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
            hash = pwd_context.hash(password)
            cursor.execute(sql,(name,email,hash,Specialization,"student"))
          return RedirectResponse("/ADM/manage_students",status_code=303)
        return templates.TemplateResponse("manage_students.html", {"request": request,  "msege": "كلمه سر غير متطابقه",  "students": students})
    elif action == "serch":
        with db_cursor(db) as cursor:
          sql = "select * from user where (full_name = %s or Specialization=%s or id=%s) and role=%s "
          cursor.execute(sql,(search,search,search,"student"))
          students = cursor.fetchall()
        return templates.TemplateResponse("manage_students.html", {"request": request, "students": students})
    elif action == "delete":
        with db_cursor(db) as cursor:
          sql = "delete from user where id=%s"
          cursor.execute(sql,(student_id,))
        return RedirectResponse("/ADM/manage_students",status_code=303)
    elif action == "edit":
        with db_cursor(db) as cursor:
          cursor.execute("SELECT id FROM user WHERE email=%s AND id != %s", (email, student_id))
          student = cursor.fetchone()
        with db_cursor(db) as cursor:
          sql = "select * from user where role = %s"
          cursor.execute(sql, ("student",))
          students = cursor.fetchall()
        if student == None:
          with db_cursor(db) as cursor:
          # فقط حدث البيانات بدون كلمة السر
            sql = "UPDATE user SET full_name=%s, email=%s, Specialization=%s WHERE id=%s"
            cursor.execute(sql, (name, email, Specialization, student_id))
          return RedirectResponse("/ADM/manage_students", status_code=303)
        return  templates.TemplateResponse("manage_students.html", {"request": request,"msege":"هذا البريد الإلكتروني موجود مسبقاً، لا يمكن استخدامه لطالب آخر!","students":students})


