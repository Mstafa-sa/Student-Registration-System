from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from auth_utils import get_current_user
from db import  get_db,db_cursor
from dotenv import load_dotenv
import os
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")

router = APIRouter()


# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/schedule", response_class=HTMLResponse)
async def index(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")
    user_email = user["email"]
    with db_cursor(db) as cursor:
      sql="select id from user where email=%s"
      cursor.execute(sql,(user_email,))
      id=cursor.fetchone()
    with db_cursor(db) as cursor:
      sql="select * from courses where id_student=%s"
      cursor.execute(sql,(id[0],))
      courses=cursor.fetchall()
    response = templates.TemplateResponse(
            "schedule.html",
            {"request": request,"courses":courses }
        )
        # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
