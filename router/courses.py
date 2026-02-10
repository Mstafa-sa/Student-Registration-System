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


router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/courses", response_class=HTMLResponse)
async def courses(request: Request):
    SECRET_KEY = "132"
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/Auth/login")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_email = payload.get("email")
        con=mysql.connector.connect(host="localhost",user="root",password="Admin@123",database="school")
        cursor = con.cursor()
        sql="select id from user where email = %s"
        cursor.execute(sql,(user_email,))
        id_student = cursor.fetchone()
        if id_student:
            sql="select * from courses where id_student = %s"
            cursor.execute(sql, (id_student[0],))
            course=cursor.fetchall()
            return templates.TemplateResponse("courses.html", {"request": request,"course":course})
        return templates.TemplateResponse("courses.html", {"request": request, })#note

    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح


@router.post("/courses", response_class=HTMLResponse)
async def courses(request: Request,Course_code:str=Form(...),Division:str=Form(...)):
    SECRET_KEY = "132"
    token = request.cookies.get("token")
    if not token:
        return RedirectResponse(url="/Auth/login")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_email = payload.get("email")
        con=mysql.connector.connect(host="localhost",user="root",password="Admin@123",database="school")
        cursor = con.cursor()
        sql="select id from user where email = %s"
        cursor.execute(sql,(user_email,))
        id_student = cursor.fetchone()
        if id_student:
            sql="select * from materials_available_for_operation where رمزالمساق = %s and القاعة =%s"
            cursor.execute(sql, (Course_code, Division))

            course=cursor.fetchone()
            sql="select * from courses where id_student = %s"
            cursor.execute(sql, (id_student[0],))
            Recorded_materials=cursor.fetchall()

            if course:
             sql="select * from courses where id_student = %s and (المادة=%s or (الوقت=%s and اليوم=%s)) "
             cursor.execute(sql, (id_student[0], course[4],course[2],course[5]))
             a=cursor.fetchone()

             if a==None:


               sql = """
                  INSERT INTO courses
                      (id_student,القاعة, الوقت, المدرس, المادة, اليوم, الساعات,رمزالمساق)
                  VALUES (%s, %s, %s, %s, %s, %s, %s,%s) \
                   """

               cursor.execute(sql, (
                id_student[0],  # id_student
                course[1],  # القاعة / رمز المساق
                course[2],  # الوقت (datetime)
                course[3],  # المدرس
                course[4],  # المادة
                course[5],  # اليوم
                course[6],  # الساعات
                course[7]   #رمز المساق

               ))

               con.commit()
               cursor.close()
               return RedirectResponse(url="/STU/courses",status_code=303)
             return templates.TemplateResponse("courses.html", {"request": request, "messages": "الماده موجوده او امسجل بنفس الوقت","course":Recorded_materials})
            return templates.TemplateResponse("courses.html", {"request": request, "messages": "الماده غير موجود من المواد المتاحه","course":Recorded_materials})



    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح

