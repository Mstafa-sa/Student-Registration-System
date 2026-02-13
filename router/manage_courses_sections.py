

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import jwt
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
import mysql.connector
from passlib.context import CryptContext

load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/manage_courses_sections", response_class=HTMLResponse)
async def manage_courses_sections(request: Request):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
    cursor = con.cursor()
    sql="select * from subject "
    cursor.execute(sql)
    subject=cursor.fetchall()

    cursor2 = con.cursor()
    sql="select * from sections "
    cursor.execute(sql)
    section=cursor.fetchall()
    cursor2.close()
    response = templates.TemplateResponse(
        "manage_courses_sections.html",
        {"request": request,"subject":subject,"section":section}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@router.post("/manage_courses_sections", response_class=HTMLResponse)
async def manage_courses_sections(request: Request,subject_code: str = Form(None),subject_name: str = Form(None),hours: int = Form(None),majors_code: str = Form(None),
                                  room:str=Form(None),time:str=Form(None),action: str = Form(...),course:int=Form(None),teacher:str=Form(None),time_today:str=Form(None),):
    if action == "addCourse":
      con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
      )

      cursor = con.cursor()
      sql="select * from subject where subject_code=%s and major_code=%s  "
      cursor.execute(sql, (subject_code,majors_code))
      subjects=cursor.fetchall()
      cursor1 = con.cursor()
      sql = "select * from subject "
      cursor1.execute(sql)
      subject = cursor.fetchall()
      cursor.close()
      cursor1.close()

      if subjects ==None:
        con = mysql.connector.connect(
              host="localhost",
              user="root",
              password=os.getenv("DB_PASSWORD"),
              database="school"
          )
        cursor = con.cursor()
        sql="insert into subject (الساعات,subject_name,subject_code,major_code) values (%s,%s,%s,%s)";
        cursor.execute(sql,(hours,subject_name,subject_code,majors_code))
        con.commit()
        cursor1=con.cursor()
        sql="select * from subject "
        cursor.execute(sql)
        subject=cursor.fetchall()

        cursor1.close()
        return templates.TemplateResponse("manage_courses_sections.html", {"request": request, "subject": subject, "messages": "تم اصافه الماده لا تنسى اضافه الشعبه"})


      return templates.TemplateResponse("manage_courses_sections.html", {"request": request, "subject": subject,  "messages": "الماده موجود لا يمكن اضافتها"})


    elif action == "addSection":

            con = mysql.connector.connect(
                host="localhost",
                user="root",
                password=os.getenv("DB_PASSWORD"),
                database="school"
            )
            cursor = con.cursor()
            sql = "insert into sections (subject_id,teacher_name,room_code,time,todays) values (%s,%s,%s,%s,%s)";
            cursor.execute(sql, ( course,teacher,room,time,time_today ))
            con.commit()
            cursor2 = con.cursor()
            sql = "select * from sections "
            cursor.execute(sql)
            section = cursor.fetchall()

            cursor2.close()
            con = mysql.connector.connect(
                host="localhost",
                user="root",
                password=os.getenv("DB_PASSWORD"),
                database="school"
            )
            cursor = con.cursor()
            sql="""SELECT
                   
                   s.subject_name,
                   s.major_code,
                   s.الساعات,
                   s.subject_code,
                   sec.room_code,
                   sec.id,
                   sec.teacher_name,
                   sec.time,
                   sec.id,
                   sec.todays
                
                   
                   FROM sections sec
                   JOIN subject s ON sec.subject_id = s.id
                  
                            """
            cursor.execute(sql)
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
                sql="insert into materials_available_for_operation (القاعة,الوقت,المدرس,المادة,اليوم,الساعات,رمزالمساق,section_id,major_code) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, ( course[4],course[7],course[6],course[0],course[9],course[2],course[3],course[8],course[1] ))
                con.commit()
                cursor.close()

                return RedirectResponse("/ADM/manage_courses_sections", status_code=303)







