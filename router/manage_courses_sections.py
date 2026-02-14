

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
    cursor2.execute(sql)
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
                                  room:str=Form(None),time:str=Form(None),action: str = Form(...),course:int=Form(None),teacher:str=Form(None),time_today:str=Form(None),course_id:int=Form(None),
                                  sections_id:int=Form(None),update_id:int=Form(None),update_name:str=Form(None),update_hours:int=Form(None),update_majors:str=Form(None),update_code:str=Form(None),
                                   update_teacher:str=Form(None),number_subject:int=Form(None),update_room:str=Form(None),update_time:str=Form(None),update_today:str=Form(None)):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
    cursor = con.cursor()
    sql = "select * from sections "
    cursor.execute(sql)
    section = cursor.fetchall()
    cursor.close()
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
    cursor = con.cursor()
    sql = "select * from subject "
    cursor.execute(sql)
    subject = cursor.fetchall()
    cursor.close()
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
      subjects=cursor.fetchone()
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
        cursor.close()
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
        sql = """
              SELECT id
              FROM sections
              WHERE time = %s
                AND (
                  room_code = %s
                 OR teacher_name = %s
                  ) and todays=%s
                   \
              """

        cursor.execute(sql, (time,room,teacher,time_today))
        section_id = cursor.fetchone()
        if section_id ==None:

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
            cursor.close()
            return  templates.TemplateResponse("manage_courses_sections.html", {"request": request, "subject": subject,"section": section})

        return templates.TemplateResponse("manage_courses_sections.html",  {"request": request, "subject": subject, "section": section,"messages":"لا يمكن إضافة الشعبة — يوجد تعارض في الوقت مع نفس القاعة أو نفس الدكتور في هذا اليوم."})
    elif action == "deleteCourse":
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="school"
        )
        cursor = con.cursor()
        sql = "delete from subject where id = %s"
        cursor.execute(sql, (course_id,))
        con.commit()
        cursor.close()
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
    elif action == "deleteSection":
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="school"
        )
        cursor = con.cursor()
        sql = "delete from sections  where id = %s"
        cursor.execute(sql, (sections_id,))
        con.commit()
        cursor.close()
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
    elif action == "updateCourse":
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="school"
        )
        cursor = con.cursor()
        sql = """update subject set   الساعات=%s , subject_name=%s , subject_code=%s , major_code=%s 
                where id = %s """
        cursor.execute(sql,(update_hours,update_name,update_code,update_majors,update_id))
        con.commit()
        cursor.close()
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
    elif action == "updateSection":
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="school"
        )
        cursor = con.cursor()
        sql = """
              SELECT id
              FROM sections
              WHERE time = %s
                AND (
                  room_code = %s
                 OR teacher_name = %s
                  ) \
                and todays=%s \
 \
              """
        cursor.execute(sql,(update_time,update_room,update_teacher,update_today))
        update_section = cursor.fetchone()
        cursor.close()
        if update_section == None:
          con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="school"
          )
          cursor = con.cursor()

          sql = """update sections set   subject_id=%s , teacher_name=%s , room_code=%s , time=%s ,todays=%s
                where id = %s """
          cursor.execute(sql,(number_subject,update_teacher,update_room,update_time,update_today,update_id))
          con.commit()
          cursor.close()
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return templates.TemplateResponse("manage_courses_sections.html",  {"request": request, "subject": subject, "section": section,"messages": "لا يمكن إضافة الشعبة — يوجد تعارض في الوقت مع نفس القاعة أو نفس الدكتور في هذا اليوم."})












