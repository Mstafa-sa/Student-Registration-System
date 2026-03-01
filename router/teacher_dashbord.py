from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
from auth_utils import get_current_user
load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/teacherDashbord", response_class=HTMLResponse)
async def index(request: Request,user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("teacherDashbord.html", {"request": request})