from fastapi import APIRouter, Request, Depends,  HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from db import  get_db,db_cursor
from dotenv import load_dotenv
import os
from auth_utils import get_current_user
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/coursesAvailable", response_class=HTMLResponse)
async def courses_available(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")

    major = user["Specialization"]
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
                   WHERE major_code=%s\
                    """
      cursor.execute(sql,(major,))
      courses = cursor.fetchall()

    response = templates.TemplateResponse(
                   "coursesAvailable.html",
                   {"request": request,"courses":courses}
                       )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

