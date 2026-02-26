from fastapi import APIRouter, Request, Cookie, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
from auth_utils import get_current_user
from db import  get_db,db_cursor
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()
templates = Jinja2Templates(directory="templates")
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")
    user_email = user["email"]
    with db_cursor(db) as cursor:
      sql = "SELECT * FROM user WHERE email = %s"
      cursor.execute(sql,(user_email,))
      id = cursor.fetchone()


    with db_cursor(db) as cursor:
      sql = "SELECT count(*), sum(hours) FROM courses WHERE id_student = %s"
      cursor.execute(sql,(id[0],))
      numbers = cursor.fetchone()

    response = templates.TemplateResponse(
            "dashboard.html",
            {"request": request,"numbers":numbers}
        )

        # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

