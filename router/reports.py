from datetime import date
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from db import get_connection
from dotenv import load_dotenv
import os
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()
num_all = (0,0,0,0)
# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/reports", response_class=HTMLResponse)
async def reports(request: Request):
    response = templates.TemplateResponse(
        "reports.html",
        {"request": request,"num_all":num_all}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response
@router.post("/reports", response_class=HTMLResponse)
async def reports(request: Request,action: str = Form(...),from_date:date=Form(...),to_date:date=Form(...)):
    num_all = (0,0,0,0)
    if action == "courses":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = """
              SELECT s.full_name, \
                     s.id, \
                     s.role,\
                     sec.hours, \
                     sec.Course_code, \
                     sec.Hall, \
                     sec.article, \
                     sec.time_s, \
                     sec.today\
                     
              FROM courses sec
                       JOIN user s ON sec.id_student = s.id 
              WHERE sec.Registration_date between %s and %s   and s.role=%s\
                  order by sec.Registration_date\
                 
                 
              """
        cursor.execute(sql,(from_date,to_date,"student"))
        students=cursor.fetchall()
        cursor.close()
        if students != []:
            con = get_connection()
            cursor = con.cursor(buffered=True)
            sql = """ \
                  SELECT COUNT(DISTINCT sec.id_student) AS students_count, \
                         count(DISTINCT sec.article)     as courses_count, \
                         COUNT(DISTINCT sec.Hall)     AS room_count, \
                         sum(sec.hours)               as clook_count \
                  FROM courses sec \
                           JOIN user s ON sec.id_student = s.id \
                  WHERE sec.Registration_date BETWEEN %s AND %s \
                    AND s.role = %s; \

                """
            cursor.execute(sql, (from_date, to_date, "student"))
            num_all = cursor.fetchone()
            cursor.close()
            return templates.TemplateResponse("reports.html",{"request": request,"students":students,"num_all":num_all})
        return templates.TemplateResponse("reports.html", {"request": request, "message":"لا يوجد مواد تم تسجيلها بهادا الوقت","num_all":num_all})
    elif action == "students":
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = """
              SELECT DISTINCT s.id,
                              s.full_name,
                              s.role,
                              s.Registration_date
              FROM user s
                       JOIN courses sec ON sec.id_student = s.id
              WHERE s.Registration_date BETWEEN %s AND %s
                AND s.role = %s
              ORDER BY s.Registration_date \
              """
        cursor.execute(sql, (from_date, to_date,"student"))
        students = cursor.fetchall()
        cursor.close()
        con = get_connection()
        cursor = con.cursor(buffered=True)
        sql = """ \
              SELECT COUNT(DISTINCT sec.id_student) AS students_count, \
                     count(DISTINCT sec.article)     as courses_count, \
                     COUNT(DISTINCT sec.Hall)     AS room_count, \
                     sum(sec.hours)               as clook_count \
              FROM courses sec \
                       JOIN user s ON sec.id_student = s.id \
              WHERE sec.Registration_date BETWEEN %s AND %s \
                AND s.role = %s; \

            """
        cursor.execute(sql, (from_date, to_date, "student"))
        num_all = cursor.fetchone()
        cursor.close()
        if students != []:
            return  templates.TemplateResponse("reports.html",{"request": request,"students":students,"num_all":num_all})
        return templates.TemplateResponse("reports.html",   {"request": request, "message": "لا يوجد طلاب تم تسجيلهم بهاذا الوقت","num_all":num_all})



