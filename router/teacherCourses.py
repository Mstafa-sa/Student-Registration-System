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
@router.get("/teacherCourses", response_class=HTMLResponse)
async def teacherCourses(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    with db_cursor(db) as cursor:
        sql="select count(article) from courses  "
    return templates.TemplateResponse("teacherCourses.html",{"request":request})
