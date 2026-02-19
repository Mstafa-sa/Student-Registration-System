
from fastapi import APIRouter, Request, Cookie, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from datetime import time
from fastapi import Form
from blacklist import BLACKLIST
from db import get_connection
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/manage_courses_sections", response_class=HTMLResponse)
async def manage_courses_sections(request: Request,token_ad:str =Cookie(None)):
    if not token_ad:
        return RedirectResponse(url="/Auth/login")
    if token_ad in BLACKLIST:
        raise HTTPException(status_code=401)
    con = get_connection()
    cursor = con.cursor(buffered=True)
    sql="select * from subject "
    cursor.execute(sql)
    subject=cursor.fetchall()
    cursor.close()
    con = get_connection()
    cursor = con.cursor(buffered=True)
    sql="select * from sections "
    cursor.execute(sql)
    section=cursor.fetchall()
    cursor.close()
    response = templates.TemplateResponse(
        "manage_courses_sections.html",
        {"request": request,"subject":subject,"section":section}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@router.post("/manage_courses_sections", response_class=HTMLResponse)
async def manage_courses_sections(request: Request,subject_code: str = Form(None),subject_name: str = Form(None),hours: int = Form(None),majors_code: str = Form(None),
                                  room:str=Form(None),from_time:time=Form(None),action: str = Form(...),course:int=Form(None),teacher:str=Form(None),time_today:str=Form(None),course_id:int=Form(None),
                                  sections_id:int=Form(None),update_id:int=Form(None),update_name:str=Form(None),update_hours:int=Form(None),update_majors:str=Form(None),update_code:str=Form(None),
                                   update_teacher:str=Form(None),number_subject:int=Form(None),update_room:str=Form(None),update_from_time:time=Form(None),update_to_time:time=Form(None),update_today:str=Form(None),to_time:time=Form(None),):
    con = get_connection()
    cursor = con.cursor(buffered=True)
    sql = "select * from sections "
    cursor.execute(sql)
    section = cursor.fetchall()
    cursor.close()
    con = get_connection()
    cursor = con.cursor(buffered=True)
    sql = "select * from subject "
    cursor.execute(sql)
    subject = cursor.fetchall()
    cursor.close()
    if action == "addCourse":
      con = get_connection()
      cursor = con.cursor(buffered=True)
      sql="select * from subject where subject_code=%s and major_code=%s  "
      cursor.execute(sql, (subject_code,majors_code))
      subjects=cursor.fetchone()
      cursor.close()
      if subjects ==None:
        con = get_connection()
        cursor = con.cursor()
        sql="insert into subject (hours,subject_name,subject_code,major_code) values (%s,%s,%s,%s)";
        cursor.execute(sql,(hours,subject_name,subject_code,majors_code))
        con.commit()
        cursor.close()
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
      return templates.TemplateResponse("manage_courses_sections.html", {"request": request, "subject": subject,  "messages": "الماده موجود لا يمكن اضافتها"})
    elif action == "addSection":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = """
              SELECT id
              FROM sections
              WHERE from_time = %s and to_time = %s
                AND (
                  room_code = %s
                 OR teacher_name = %s
                  ) and todays=%s
                   \
              """

        cursor.execute(sql, (from_time,to_time,room,teacher,time_today))
        section_id = cursor.fetchone()
        cursor.close()
        if section_id ==None:
            con = get_connection()
            cursor = con.cursor()
            sql = "insert into sections (subject_id,teacher_name,room_code,from_time,to_time,todays) values (%s,%s,%s,%s,%s,%s)";
            cursor.execute(sql, ( course,teacher,room,from_time,to_time,time_today ))
            con.commit()
            cursor.close()
            return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return templates.TemplateResponse("manage_courses_sections.html",  {"request": request, "subject": subject, "section": section,"messages":"لا يمكن إضافة الشعبة — يوجد تعارض في الوقت مع نفس القاعة أو نفس الدكتور في هذا اليوم."})
    elif action == "deleteCourse":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = "select * from subject where id = %s"
        cursor.execute(sql, (course_id,))
        course_all = cursor.fetchone()
        cursor.close()
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = """SELECT id
                 FROM courses
                 WHERE hours = %s \
                   AND article = %s \
                   AND Course_code = %s"""
        cursor.execute(sql, (course_all[1], course_all[2].strip(), course_all[3].strip()))
        courseId = cursor.fetchone()
        cursor.close()
        con = get_connection()
        cursor = con.cursor()
        sql = "delete from subject where id = %s"
        cursor.execute(sql, (course_id,))
        con.commit()
        cursor.close()
        if courseId :
          con = get_connection()
          cursor = con.cursor()
          sql="update courses set materialIsAvailable = %s where id = %s"
          cursor.execute(sql, ("لا", courseId[0]))
          con.commit()
          cursor.close()
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
    elif action == "deleteSection":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = "select * from sections where id = %s"
        cursor.execute(sql, (sections_id,))
        course_all = cursor.fetchone()
        cursor.close()
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = """select id \
                 from courses \
                 where teacher = %s \
                   and Hall = %s \
                   and from_time = %s \
                   and today = %s 
                     and to_time=%s"""
        cursor.execute(sql, (course_all[2], course_all[3], course_all[4], course_all[5],course_all[6]))
        courseId = cursor.fetchone()
        cursor.close()
        con = get_connection()
        cursor = con.cursor()
        sql = "delete from sections  where id = %s"
        cursor.execute(sql, (sections_id,))
        con.commit()
        cursor.close()
        if courseId :
          con = get_connection()
          cursor = con.cursor()
          sql="update courses set materialIsAvailable = %s where id = %s"
          cursor.execute(sql, ("لا", courseId[0]))
          con.commit()
          cursor.close()
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
    elif action == "updateCourse":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql="select id from subject where id != %s and subject_code=%s and major_code=%s"
        cursor.execute(sql,(update_id,update_code,update_majors))
        update_course=cursor.fetchone()
        if update_course ==None:
          con = get_connection()
          cursor = con.cursor(buffered=True)
          sql="select * from subject where id = %s"
          cursor.execute(sql,(update_id,))
          subject_all = cursor.fetchone()
          cursor.close()
          con = get_connection()
          cursor = con.cursor(buffered=True)
          sql = """SELECT id
                   FROM courses
                   WHERE hours = %s \
                     AND article = %s \
                     AND Course_code = %s"""
          cursor.execute(sql, (subject_all[1], subject_all[2].strip(),subject_all[3].strip()))
          course_id = cursor.fetchone()
          cursor.close()
          con = get_connection()
          cursor = con.cursor()
          sql = """update subject set   hours=%s , subject_name=%s , subject_code=%s , major_code=%s 
                where id = %s """
          cursor.execute(sql,(update_hours,update_name.strip(),update_code.strip(),update_majors.strip(),update_id))
          con.commit()
          cursor.close()
          if course_id :
            con = get_connection()
            cursor = con.cursor()
            sql="update courses set  hours=%s , article=%s , Course_code=%s  where id = %s"
            cursor.execute(sql,(update_hours,update_name.strip(),update_code.strip(),course_id[0]))
            con.commit()
            cursor.close()
            return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return templates.TemplateResponse("manage_courses_sections.html", {"request": request, "subject": subject, "section": section, "messages": "الماده موجود لا يمكن اضافتها"})
    elif action == "updateSection":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = """
              SELECT id
              FROM sections
              WHERE from_time = %s and to_time = %s
                AND (
                  room_code = %s
                 OR teacher_name = %s
                  ) \
                and todays=%s \
 \
              """
        cursor.execute(sql,(update_from_time,update_to_time,update_room,update_teacher,update_today))
        update_section = cursor.fetchone()
        cursor.close()
        print(update_section)
        if update_section == None:
          con = get_connection()
          cursor = con.cursor(buffered=True)
          sql = "select * from sections where id = %s"
          cursor.execute(sql, (update_id,))
          subject_all = cursor.fetchone()
          cursor.close()
          con = get_connection()
          cursor = con.cursor(buffered=True)
          sql = """select id from courses where teacher=%s and Hall=%s and from_time=%s and today=%s and to_time=%s """
          cursor.execute(sql,(subject_all[2],subject_all[3],subject_all[4],subject_all[5],subject_all[6]))
          course_id = cursor.fetchone()
          cursor.close()
          con = get_connection()
          cursor = con.cursor()

          sql = """update sections set   subject_id=%s , teacher_name=%s , room_code=%s , from_time=%s ,todays=%s,to_time=%s
                where id = %s """
          cursor.execute(sql,(number_subject,update_teacher,update_room,update_from_time,update_today,update_to_time,update_id))
          con.commit()
          cursor.close()
          con = get_connection()
          cursor = con.cursor()
          if course_id :
            sql="update courses set teacher=%s , Hall=%s , from_time=%s ,today=%s,to_time=%s where id= %s "
            cursor.execute(sql,(update_teacher,update_room,update_from_time,update_today,update_to_time,course_id[0]))
            con.commit()
            cursor.close()
            return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return templates.TemplateResponse("manage_courses_sections.html",  {"request": request, "subject": subject, "section": section,"messages": "لا يمكن إضافة الشعبة — يوجد تعارض في الوقت مع نفس القاعة أو نفس الدكتور في هذا اليوم."})












