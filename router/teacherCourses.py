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
    email = user["email"]
    with db_cursor(db) as cursor:
        sql = "select t.id from user u join teacher t on u.id=t.id_user where u.email=%s"
        cursor.execute(sql, (email,))
        id_teacher = cursor.fetchone()
    with db_cursor(db) as cursor:
        sql="""select s.subject_name,
           count(distinct sec.id) as total_sections,
           count(distinct c.id_student) as total_students
    from subject s
    join teacher_subject t on t.id_subject = s.id
    join sections sec on sec.subject_id = s.id
    left join courses c 
           on c.id_teacher = t.id_user
           and c.id_subject = s.id
    where t.id_user = %s
    group by s.id, s.subject_name """
        cursor.execute(sql, (id_teacher[0],))
        num_subject=cursor.fetchall()

    return templates.TemplateResponse("teacherCourses.html",{"request":request,"num_subject":num_subject})
