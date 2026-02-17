from datetime import date

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import mysql.connector
import jwt
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/reports", response_class=HTMLResponse)
async def reports(request: Request):
    response = templates.TemplateResponse(
        "reports.html",
        {"request": request}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response
@router.post("/reports", response_class=HTMLResponse)
async def reports(request: Request,action: str = Form(...),from_date:date=Form(...),to_date:date=Form(...)):
    if action == "courses":
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="school"
        )
        cursor = con.cursor()
        sql = """
              SELECT s.full_name, \
                     s.id, \
                     s.role,\
                     sec.الساعات, \
                     sec.رمزالمساق, \
                     sec.القاعة, \
                     sec.المادة, \
                     sec.الوقت, \
                     sec.اليوم
              FROM courses sec
                       JOIN user s ON sec.id_student = s.id 
              WHERE sec.Registration_date between %s and %s   and s.role=%s\
                  order by sec.Registration_date\
                 
              """
        cursor.execute(sql,(from_date,to_date,"Admin"))
        students=cursor.fetchall()
        print(students)
        if students != []:
            print(students[0][0])
            print(students[0][1])
            print(students[0][2])
            print(students[0][3])
            print(students[0][4])
            print(students[0][5])
            print(students[0][6])
            print(students[0][7])
            return templates.TemplateResponse("reports.html",{"request": request,"students":students})
        return templates.TemplateResponse("reports.html", {"request": request, "message":"لا يوجد مواد تم تسجيلها بهادا الوقت"})
    elif action == "students":
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("DB_PASSWORD"),
            database="school"
        )
        cursor = con.cursor()
        sql = """
              SELECT s.full_name,
                     s.id,
                     s.role,
                     sec.الساعات,
                     sec.رمزالمساق,
                     sec.القاعة,
                     sec.المادة,
                     sec.الوقت,
                     sec.اليوم,
                     s.Registration_date
              FROM courses sec
                       JOIN user s ON sec.id_student = s.id
              WHERE s.Registration_date BETWEEN %s AND %s
                AND s.role = %s
              ORDER BY s.Registration_date \
              """

        cursor.execute(sql, (from_date, to_date, "student"))
        students = cursor.fetchall()
        print(students)
        if students != []:
            print(students[0][0])
            print(students[0][1])
            print(students[0][2])
            print(students[0][3])
            print(students[0][4])
            print(students[0][5])
            print(students[0][6])
            print(students[0][7])


