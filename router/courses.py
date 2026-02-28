from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from auth_utils import get_current_user
from db import  get_db,db_cursor
from fastapi import Depends, HTTPException
from datetime import datetime
load_dotenv()  # ← تقرأ ملف .env

secret_key = os.getenv("JWT_SECRET")
now=datetime.now()

router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/courses", response_class=HTMLResponse)
async def courses(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")
    user_email =user["email"]
    with db_cursor(db) as cursor:
      sql="select id from user where email = %s"
      cursor.execute(sql,(user_email,))
      id_student = cursor.fetchone()
    if id_student:
            with db_cursor(db) as cursor:
              sql="select * from courses where id_student = %s"
              cursor.execute(sql, (id_student[0],))
              course=cursor.fetchall()

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

@router.post("/courses", response_class=HTMLResponse)
async def courses(request: Request,Course_code:str=Form(None),Division:str=Form(None)
                  ,method: str = Form(...),id:list[int]=Form(None),user: dict = Depends(get_current_user),db=Depends(get_db)):
    if method == "post":
        if user["role"] != "student":
            raise HTTPException(status_code=403, detail="Access denied")
        user_email = user["email"]
        major=user["Specialization"]
        with db_cursor(db) as cursor:
          sql="select id from user where email = %s"
          cursor.execute(sql,(user_email,))
          id_student = cursor.fetchone()
        if id_student:
             with db_cursor(db) as cursor:
               sql = "select * from courses where id_student = %s"
               cursor.execute(sql, (id_student[0],))
               Recorded_materials = cursor.fetchall()
             if Course_code and Division:
               with db_cursor(db) as cursor:
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
                            sec.to_time,
                            sec.number_of_seats
                     FROM sections sec
                              JOIN subject s ON sec.subject_id = s.id
                     WHERE s.subject_code = %s
                       AND sec.room_code = %s \
                         and  s.major_code=%s
                     """
                 cursor.execute(sql,(Course_code, Division,major))
                 course=cursor.fetchone()# name
               if course:
                number_seat = course[10]
                with db_cursor(db) as cursor:
                  sql="""SELECT *
                        FROM courses
                        WHERE id_student = %s
                          AND today = %s
                          AND NOT (to_time <= %s OR from_time >= %s)
 """
                  cursor.execute(sql, (id_student[0], course[8],course[7],course[9]))
                  a=cursor.fetchone()
                if a==None:
                  with db_cursor(db) as cursor:
                    sql="select sum(hours) from courses where id_student=%s"
                    cursor.execute(sql, (id_student[0],))
                    sum_time=cursor.fetchone()
                  if sum_time[0] is None:
                      sum_time=(0,)
                  if sum_time[0]+course[2] <=21 :
                    if number_seat == 0:
                        return templates.TemplateResponse("courses.html", {"request": request,
                                                                           "messages": "لا يوجد عدد مقاعد متاحه لتسجيل ",
                                                                           "course": Recorded_materials})
                    with db_cursor(db) as cursor:
                        sql="select * from registration_time reg join major m on  reg.id_major=m.id where  m.major_name=%s and (now() BETWEEN reg_start1 and reg_end1 or  now() BETWEEN reg_start2 and reg_end2 or now() BETWEEN reg_start3 and reg_end3) "
                        cursor.execute(sql, (major,))
                        true=cursor.fetchone()
                    if true == None:
                        return templates.TemplateResponse("courses.html", {"request": request,
                                                                           "messages": "انتهى موعد التسجيل ",
                                                                           "course": Recorded_materials})
                    with db_cursor(db) as cursor:
                      sql = """
                      INSERT INTO courses
                          (id_student,materialIsAvailable,Hall, from_time, teacher, article, today, hours,Course_code,to_time)
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
                         course[9],
                        ))
                    with db_cursor(db) as cursor:
                      cursor.execute("update sections set number_of_seats=number_of_seats-1 where  room_code = %s and from_time=%s and to_time=%s and todays=%s ",
                                   ( Division,course[7],course[9],course[8]))
                    return RedirectResponse(url="/STU/courses",status_code=303)
                  return templates.TemplateResponse("courses.html", {"request": request, "messages": "لا تستطيع التسجيل اكثر من 21 ساعه",  "course": Recorded_materials})
                return templates.TemplateResponse("courses.html", {"request": request, "messages": "الماده موجوده او امسجل بنفس الوقت","course":Recorded_materials})
               return templates.TemplateResponse("courses.html", {"request": request, "messages": "الماده غير موجود من المواد المتاحه","course":Recorded_materials})
             return templates.TemplateResponse("courses.html",{"request": request, "messages": "الرجاء تعبئة جميع الحقول المطلوبة",  "course": Recorded_materials})
    elif method=="delete":
      if id == None:
          return RedirectResponse(url="/STU/courses", status_code=303)
      for i in id:
        with db_cursor(db) as cursor:
          sql="select * from courses where id = %s"
          cursor.execute(sql, (id[0],))
          course=cursor.fetchone()
        with db_cursor(db) as cursor:
          sql = "delete from courses where id = %s"
          cursor.execute(sql, (i,))
        with db_cursor(db) as cursor:
          cursor.execute(
            "update sections set number_of_seats=number_of_seats+1 where  room_code = %s and from_time=%s and to_time=%s and todays=%s ",
            ( course[2], course[3], course[11], course[6]))
      return RedirectResponse(url="/STU/courses", status_code=303)
