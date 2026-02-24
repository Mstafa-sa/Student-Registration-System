from fastapi import APIRouter, Request, Cookie, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

from starlette.responses import RedirectResponse

from auth_utils import get_current_user
from blacklist import BLACKLIST

load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/Admin_Dashboard", response_class=HTMLResponse)
async def Admin_Dashboard(request: Request,user: dict = Depends(get_current_user)):
    if user["role"] != "Admin":
        raise HTTPException(status_code=403, detail="Access denied")
    response = templates.TemplateResponse(
        "Admin_Dashboard.html",
        {"request": request}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response