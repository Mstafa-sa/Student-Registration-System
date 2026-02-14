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
@router.get("/courses", response_class=HTMLResponse)
async def courses(request: Request):

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
        sql="select id from user where email = %s"
        cursor.execute(sql,(user_email,))
        id_student = cursor.fetchone()
        if id_student:
            sql="select * from courses where id_student = %s"
            cursor.execute(sql, (id_student[0],))
            course=cursor.fetchall()
            response = templates.TemplateResponse(
                "courses.html",
                {"request": request,"course":course}
            )

            # 🔥 منع الكاش
            response.headers["Cache-Control"] = "no-store"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
        return templates.TemplateResponse("courses.html", {"request": request, })#note

    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/Auth/login")  # التوكن انتهى
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح


@router.post("/courses", response_class=HTMLResponse)
async def courses(request: Request,Course_code:str=Form(None),Division:str=Form(None),method: str = Form(...),id:list[int]=Form(None)):

    if method=="post":


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
         sql="select id from user where email = %s"
         cursor.execute(sql,(user_email,))
         id_student = cursor.fetchone()
         if id_student:
             sql = "select * from courses where id_student = %s"
             cursor.execute(sql, (id_student[0],))
             Recorded_materials = cursor.fetchall()
             cursor.close()
             if Course_code and Division:
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
                     WHERE s.subject_code = %s
                       AND sec.room_code = %s \
                     """

               cursor.execute(sql,(Course_code, Division))
               course=cursor.fetchone()# name
               cursor.fetchall()
               cursor.close()
               if course:
                con = mysql.connector.connect(
                       host="localhost",
                       user="root",
                       password=os.getenv("DB_PASSWORD"),
                       database="school"
                   )
                cursor = con.cursor()
                sql="select * from courses where id_student = %s and (المادة=%s or (الوقت=%s and اليوم=%s)) "
                cursor.execute(sql, (id_student[0], course[4],course[2],course[5]))
                a=cursor.fetchone()
                cursor.close()
                if a==None:
                  con = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password=os.getenv("DB_PASSWORD"),
                        database="school"
                    )
                  cursor = con.cursor()
                  sql="select sum(الساعات) from courses where id_student=%s"
                  cursor.execute(sql, (id_student[0],))
                  sum_time=cursor.fetchone()
                  if sum_time[0]+course[2] <=21 :
                    print(sum_time[0])

                    sql = """
                      INSERT INTO courses
                          (id_student,القاعة, الوقت, المدرس, المادة, اليوم, الساعات,رمزالمساق)
                      VALUES (%s, %s, %s, %s, %s, %s, %s,%s) \
                       """

                    cursor.execute(sql, (
                     id_student[0],  # id_student
                     course[4],  # القاعة
                     course[7],  # الوقت (datetime)
                     course[6],  # المدرس
                     course[0],  # المادة
                     course[8],  # اليوم
                     course[2],  # الساعات
                     course[3]   #رمز المساق

                    ))

                    con.commit()
                    cursor.close()
                    return RedirectResponse(url="/STU/courses",status_code=303)
                  return templates.TemplateResponse("courses.html", {"request": request, "messages": "لا تستطيع التسجيل اكثر من 21 ساعه",  "course": Recorded_materials})
                return templates.TemplateResponse("courses.html", {"request": request, "messages": "الماده موجوده او امسجل بنفس الوقت","course":Recorded_materials})
               return templates.TemplateResponse("courses.html", {"request": request, "messages": "الماده غير موجود من المواد المتاحه","course":Recorded_materials})
             return templates.TemplateResponse("courses.html",{"request": request, "messages": "الرجاء تعبئة جميع الحقول المطلوبة",  "course": Recorded_materials})





     except jwt.ExpiredSignatureError:
         return RedirectResponse(url="/Auth/login")  # التوكن انتهى
     except jwt.InvalidTokenError:
         return RedirectResponse(url="/Auth/login")  # التوكن غير صحيح
    elif method=="delete":

        con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
        cursor = con.cursor()
        sql = "delete from courses where id = %s"
        for i in id:
         cursor.execute(sql, (i,))
        con.commit()
        cursor.close()
        return RedirectResponse(url="/STU/courses", status_code=303)
