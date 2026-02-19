from fastapi import APIRouter, Request, Depends, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import jwt
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

from blacklist import BLACKLIST
from db import get_connection
from fastapi import Depends, HTTPException
load_dotenv()  # ← تقرأ ملف .env

secret_key = os.getenv("JWT_SECRET")


router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/courses", response_class=HTMLResponse)
async def courses(request: Request,token:str =Cookie(None)):
    if not token:
        return RedirectResponse(url="/Auth/login")
    if token in BLACKLIST:
        raise HTTPException(status_code=401)
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        user_email = payload.get("email")
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql="select id from user where email = %s"
        cursor.execute(sql,(user_email,))
        id_student = cursor.fetchone()
        cursor.close()
        if id_student:
            con = get_connection()
            cursor = con.cursor(buffered=True)
            sql="select * from courses where id_student = %s"
            cursor.execute(sql, (id_student[0],))
            course=cursor.fetchall()
            cursor.close()
            response = templates.TemplateResponse(
                "courses.html",
                {"request": request,"course":course}
            )

            # 🔥 منع الكاش
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
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
         con = get_connection()
         cursor = con.cursor(buffered=True)
         sql="select id from user where email = %s"
         cursor.execute(sql,(user_email,))
         id_student = cursor.fetchone()
         cursor.close()
         if id_student:
             con = get_connection()
             cursor = con.cursor(buffered=True)
             sql = "select * from courses where id_student = %s"
             cursor.execute(sql, (id_student[0],))
             Recorded_materials = cursor.fetchall()
             cursor.close()
             if Course_code and Division:
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

                con = get_connection()
                cursor = con.cursor(buffered=True)
                sql="select * from courses where id_student = %s and (article =%s or (from_time=%s and today=%s)) "##################
                cursor.execute(sql, (id_student[0], course[4],course[7],course[8]))
                a=cursor.fetchone()
                cursor.close()

                if a==None:
                  con = get_connection()
                  cursor = con.cursor(buffered=True)
                  sql="select sum(hours) from courses where id_student=%s"
                  cursor.execute(sql, (id_student[0],))
                  sum_time=cursor.fetchone()
                  cursor.close()
                  if sum_time[0] == None:
                      sum_time=(0,)
                  if sum_time[0]+course[2] <=21 :
                    con = get_connection()
                    cursor = con.cursor()
                    sql = """
                      INSERT INTO courses
                          (id_student,materialIsAvailable,Hall, from_time, teacher, article, today, hours,Course_code,to_time)####################
                      VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s,%s) \
                       """
                    cursor.execute(sql, (
                     id_student[0], # id_student
                     "نعم",
                     course[4],  # القاعة
                     course[7],  # الوقت (datetime)
                     course[6],  # المدرس
                     course[0],  # المادة
                     course[8],  # اليوم
                     course[2],  # الساعات
                     course[3],#رمز المساق
                     course[11],
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
      for i in id:
        con = get_connection()
        cursor = con.cursor()
        sql = "delete from courses where id = %s"
        cursor.execute(sql, (i,))
        con.commit()
        cursor.close()
        return RedirectResponse(url="/STU/courses", status_code=303)
