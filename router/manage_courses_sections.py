
from fastapi import APIRouter, Request, Cookie, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from datetime import time
from fastapi import Form
from auth_utils import get_current_user
from db import  get_db,db_cursor
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/manage_courses_sections", response_class=HTMLResponse)
async def manage_courses_sections(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    if user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")
    with db_cursor(db) as cursor:
        sql="select t.id,u.full_name from user u join teacher t on u.id=t.id_user  "
        cursor.execute(sql)
        teachers=cursor.fetchall()

    with db_cursor(db) as cursor:
        sql="select * from major  "
        cursor.execute(sql)
        majors = cursor.fetchall()
    with db_cursor(db) as cursor:
      sql="select * from subject "
      cursor.execute(sql)
      subject=cursor.fetchall()
    with db_cursor(db) as cursor:
       sql="""SELECT 
    s.id,
    s.subject_id,
    u.full_name,
    s.room_code,
    s.from_time,
    s.todays,
    s.to_time,
    s.number_of_seats,
    s.division       
FROM sections s
JOIN teacher t ON t.id = s.teacher_id
JOIN `user` u ON u.id = t.id_user; """
       cursor.execute(sql)
       section=cursor.fetchall()

    response = templates.TemplateResponse(
        "manage_courses_sections.html",
        {"request": request,"subject":subject,"section":section,"majors":majors,"teachers":teachers}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
@router.post("/manage_courses_sections", response_class=HTMLResponse)
async def manage_courses_sections(request: Request,subject_code: str = Form(None),subject_name: str = Form(None),hours: int = Form(None),majors_code: str = Form(None),user: dict = Depends(get_current_user),
                                  room:str=Form(None),from_time:time=Form(None),action: str = Form(...),course:int=Form(None),teacher:str=Form(None),time_today:str=Form(None),course_id:int=Form(None),
                                  sections_id:int=Form(None),update_id:int=Form(None),update_name:str=Form(None),update_hours:int=Form(None),update_majors:str=Form(None),update_code:str=Form(None),
                                   update_teacher:str=Form(None),number_subject:int=Form(None),update_room:str=Form(None),update_from_time:time=Form(None),update_to_time:time=Form(None),update_today:str=Form(None),
                                  number_seat:int=Form(None),to_time:time=Form(None),division:int=Form(None),db=Depends(get_db)):
    if user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")
    with db_cursor(db) as cursor:
        sql="select t.id,u.full_name from user u join teacher t on u.id=t.id_user  "
        cursor.execute(sql)
        teachers=cursor.fetchall()

    with db_cursor(db) as cursor:
        sql="select * from major  "
        cursor.execute(sql)
        majors = cursor.fetchall()

    with db_cursor(db) as cursor:

            sql = """SELECT s.id,
                       s.subject_id,
                       u.full_name,
                       s.room_code,
                       s.from_time,
                       s.todays,
                       s.to_time,
                       s.number_of_seats,
                        s.division   
                   FROM sections s
                            JOIN teacher t ON t.id = s.teacher_id
                            JOIN `user` u ON u.id = t.id_user; """
            cursor.execute(sql)
            section=cursor.fetchall()
    with db_cursor(db) as cursor:
      sql = "select * from subject "
      cursor.execute(sql)
      subject = cursor.fetchall()
    if action == "addCourse":
      with db_cursor(db) as cursor:
        sql="select * from subject where subject_code=%s and major_code=%s  "
        cursor.execute(sql, (subject_code,majors_code))
        subjects=cursor.fetchone()
      if subjects ==None:
        with db_cursor(db) as cursor:
          sql="insert into subject (hours,subject_name,subject_code,major_code) values (%s,%s,%s,%s)";
          cursor.execute(sql,(hours,subject_name,subject_code,majors_code))
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
      return templates.TemplateResponse("manage_courses_sections.html", {"request": request, "subject": subject,"section":section, "majors":majors,"teachers":teachers, "messages": "الماده موجود لا يمكن اضافتها"})
    elif action == "addSection":
        with db_cursor(db) as cursor:
          sql = """
              SELECT id
                    FROM sections
                    WHERE
                        (
                            %s < to_time
                            AND %s > from_time
                        )
                    AND (
                            room_code = %s
                            OR teacher_id = %s
                        )
                    AND todays = %s
                  
                                  """

          cursor.execute(sql, (from_time,to_time,room,teacher,time_today))
          section_id = cursor.fetchone()
        if section_id ==None:
            with db_cursor(db) as cursor:
                sql="select id from subject where id=%s  "
                cursor.execute(sql, (course,))
                id_subject=cursor.fetchone()
            if id_subject ==None:
                return templates.TemplateResponse(
                    "manage_courses_sections.html",
                    {
                        "request": request,
                        "subject": subject,
                        "section": section,
                        "majors": majors,
                        "teachers": teachers,
                        "messages": "هده الماده غير موجوده"
                    }
                )
            with db_cursor(db) as cursor:
                sql = "SELECT id FROM sections WHERE subject_id = %s AND division = %s"
                cursor.execute(sql, (course, division))
                duplicate_division = cursor.fetchone()
            if duplicate_division:
                return templates.TemplateResponse(
                    "manage_courses_sections.html",
                    {
                        "request": request,
                        "subject": subject,
                        "section": section,
                        "majors": majors,
                        "teachers":teachers,
                        "messages": "هذه الشعبة موجودة مسبقاً لنفس المادة"
                    }
                )
            if from_time >= to_time:
                return templates.TemplateResponse("manage_courses_sections.html", {"request": request, "subject": subject, "section": section, "messages": "ضيف الوقت بشكل صحيح"})
            with db_cursor(db) as cursor:
                sql = "SELECT id FROM sections WHERE subject_id = %s AND division = %s"
                cursor.execute(sql, (course, division))
                duplicate_division = cursor.fetchone()
            if duplicate_division:
                return templates.TemplateResponse(
                    "manage_courses_sections.html",
                    {
                        "request": request,
                        "subject": subject,
                        "section": section,
                        "majors": majors,
                        "teachers": teachers,
                        "messages": "هذه الشعبة موجودة مسبقاً لنفس المادة"
                    }
                )
            with db_cursor(db) as cursor:
                sql = "insert into  teacher_subject (id_user,id_subject) values (%s,%s)"
                cursor.execute(sql, (teacher,course))
            with db_cursor(db) as cursor:
              sql = "insert into sections (subject_id,room_code,from_time,to_time,todays,number_of_seats,teacher_id,division) values (%s,%s,%s,%s,%s,%s,%s,%s) ";
              cursor.execute(sql, ( course,room,from_time,to_time,time_today,number_seat,teacher,division))
            return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return templates.TemplateResponse("manage_courses_sections.html",  {"request": request, "subject": subject, "section": section,"majors": majors,    "teachers":teachers,"messages":"لا يمكن إضافة الشعبة — يوجد تعارض في الوقت مع نفس القاعة أو نفس الدكتور في هذا اليوم."})
    elif action == "deleteCourse":
        with db_cursor(db) as cursor:
          sql = "select * from subject where id = %s"
          cursor.execute(sql, (course_id,))
          course_all = cursor.fetchone()
        with db_cursor(db) as cursor:
          sql = """SELECT id
                 FROM courses
                 WHERE hours = %s \
                   AND article = %s \
                   AND Course_code = %s"""
          cursor.execute(sql, (course_all[1], course_all[2].strip(), course_all[3].strip()))
          courseId = cursor.fetchone()
        with db_cursor(db) as cursor:
          sql = "delete from subject where id = %s"
          cursor.execute(sql, (course_id,))
        if courseId :
          with db_cursor(db) as cursor:
            sql="update courses set materialIsAvailable = %s where id = %s"
            cursor.execute(sql, ("لا", courseId[0]))
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
    elif action == "deleteSection":
        with db_cursor(db) as cursor:
          sql = "select * from sections where id = %s"
          cursor.execute(sql, (sections_id,))
          course_all = cursor.fetchone()
        with db_cursor(db) as cursor:
          sql = """select id \
                 from courses \
                 where id_teacher = %s \
                   and Hall = %s \
                   and from_time = %s \
                   and today = %s 
                     and to_time=%s"""
          cursor.execute(sql, (course_all[8], course_all[3], course_all[4], course_all[5],course_all[6]))
          courseId = cursor.fetchone()
        with db_cursor(db) as cursor:
          sql = "delete from sections  where id = %s"
          cursor.execute(sql, (sections_id,))

        with db_cursor(db) as cursor:
            sql = "delete from teacher_subject  where id_user = %s and id_subject = %s"#######################
            cursor.execute(sql, (course_all[8],course_all[1]))
        if courseId :
          with db_cursor(db) as cursor:
            sql="update courses set materialIsAvailable = %s where id = %s"
            cursor.execute(sql, ("لا", courseId[0]))
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
    elif action == "updateCourse":
        with db_cursor(db) as cursor:
          sql="select id from subject where id != %s and subject_code=%s and major_code=%s"
          cursor.execute(sql,(update_id,update_code,update_majors))
          update_course=cursor.fetchone()
        if update_course ==None:
          with db_cursor(db) as cursor:
            sql="select * from subject where id = %s"
            cursor.execute(sql,(update_id,))
            subject_all = cursor.fetchone()
          with db_cursor(db) as cursor:
            sql = """SELECT id
                   FROM courses
                   WHERE hours = %s \
                     AND article = %s \
                     AND Course_code = %s"""
            cursor.execute(sql, (subject_all[1], subject_all[2].strip(),subject_all[3].strip()))
            course_id = cursor.fetchone()
          with db_cursor(db) as cursor:
            sql = """update subject set   hours=%s , subject_name=%s , subject_code=%s , major_code=%s 
                where id = %s """
            cursor.execute(sql,(update_hours,update_name.strip(),update_code.strip(),update_majors.strip(),update_id))
          if course_id :

            with db_cursor(db) as cursor:
              sql="update courses set  hours=%s , article=%s , Course_code=%s  where id = %s"
              cursor.execute(sql,(update_hours,update_name.strip(),update_code.strip(),course_id[0]))
            return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return templates.TemplateResponse("manage_courses_sections.html", {"request": request, "subject": subject, "section": section,"majors": majors,"teachers":teachers, "messages": "الماده موجود لا يمكن اضافتها"})
    elif action == "updateSection":
        with db_cursor(db) as cursor:
          sql = """
              SELECT id
                        FROM sections
                        WHERE
                            (
                                %s < to_time
                                AND %s > from_time
                            )
                        AND (
                                room_code = %s
                                OR teacher_id = %s
                            )
                        AND todays = %s
                          AND id != %s
                                      """
          cursor.execute(sql,(update_from_time,update_to_time,update_room,update_teacher,update_today,update_id))
          update_section = cursor.fetchone()

        if update_section == None:
          with db_cursor(db) as cursor:
                sql = "select id from subject where id=%s  "
                cursor.execute(sql, (number_subject,))
                id_subject = cursor.fetchone()
          if id_subject == None:
                return templates.TemplateResponse(
                    "manage_courses_sections.html",
                    {
                        "request": request,
                        "subject": subject,
                        "section": section,
                        "majors": majors,
                        "teachers": teachers,
                        "messages": "هده الماده غير موجوده"
                    }
                )
          with db_cursor(db) as cursor:
            sql = "select * from sections where id = %s"
            cursor.execute(sql, (update_id,))
            subject_all = cursor.fetchone()
          with db_cursor(db) as cursor:
              sql = "SELECT id FROM sections WHERE subject_id = %s AND division = %s"
              cursor.execute(sql, (number_subject, division))
              duplicate_division = cursor.fetchone()
          if duplicate_division:
              return templates.TemplateResponse(
                  "manage_courses_sections.html",
                  {
                      "request": request,
                      "subject": subject,
                      "section": section,
                      "majors": majors,
                      "teachers": teachers,
                      "messages": "هذه الشعبة موجودة مسبقاً لنفس المادة"
                  }
              )
          if update_from_time==None or update_to_time== None:
              return templates.TemplateResponse("manage_courses_sections.html",   {"request": request, "subject": subject, "section": section,"majors": majors,"teachers":teachers, "messages": "ضيف الوقت بشكل صحيح"})
          if   update_from_time >= update_to_time:
              return templates.TemplateResponse("manage_courses_sections.html",  {"request": request, "subject": subject, "section": section,"majors": majors,"teachers":teachers, "messages": "ضيف الوقت بشكل صحيح"})

          if subject_all[8] != update_teacher :

             with db_cursor(db) as cursor:
                 sql = "update teacher_subject set id_user=%s where id_subject=%s and id_user=%s "
                 cursor.execute(sql, (update_teacher, subject_all[1],subject_all[8]))
          with db_cursor(db) as cursor:
            sql = """select id from courses where id_teacher=%s and Hall=%s and from_time=%s and today=%s and to_time=%s and division=%s """
            cursor.execute(sql,(subject_all[8],subject_all[3],subject_all[4],subject_all[5],subject_all[6],subject_all[8]))
            course_id = cursor.fetchone()
          with db_cursor(db) as cursor:
            sql = """update sections set   subject_id=%s , teacher_id=%s , room_code=%s , from_time=%s ,todays=%s,to_time=%s,number_of_seats=%s,division=%s
                where id = %s """
            cursor.execute(sql,(number_subject,update_teacher,update_room,update_from_time,update_today,update_to_time,number_seat,division,update_id))
          if course_id :
            with db_cursor(db) as cursor:
              sql="update courses set id_teacher=%s , Hall=%s , from_time=%s ,today=%s,to_time=%s,division=%s where id= %s "
              cursor.execute(sql,(update_teacher,update_room,update_from_time,update_today,update_to_time,division,course_id[0]))
            return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
          return RedirectResponse("/ADM/manage_courses_sections", status_code=303)
        return templates.TemplateResponse("manage_courses_sections.html",  {"request": request, "subject": subject, "section": section,"majors": majors,"teachers":teachers,"messages": "لا يمكن إضافة الشعبة — يوجد تعارض في الوقت مع نفس القاعة أو نفس الدكتور في هذا اليوم."})












