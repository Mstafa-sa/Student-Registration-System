from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
from auth_utils import get_current_user
from db import get_db, db_cursor

load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/teacherDashbord", response_class=HTMLResponse)
async def index(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    email = user["email"]
    with db_cursor(db) as cursor:
        sql="select t.id from user u join teacher t on u.id=t.id_user where u.email=%s"
        cursor.execute(sql,(email,))
        id_teacher = cursor.fetchone()
    with db_cursor(db) as cursor:
        sql="select count(id_user) from teacher_subject where id_user=%s"
        cursor.execute(sql,(id_teacher[0],))
        number_subject = cursor.fetchone()

    return templates.TemplateResponse("teacherDashbord.html", {"request": request,"number_subject":number_subject})