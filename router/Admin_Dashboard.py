from fastapi import APIRouter, Request, Cookie, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

from starlette.responses import RedirectResponse

from blacklist import BLACKLIST

load_dotenv()  # ← تقرأ ملف .env
secret_key = os.getenv("JWT_SECRET")
router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/Admin_Dashboard", response_class=HTMLResponse)
async def Admin_Dashboard(request: Request,token_ad: str = Cookie(None)):
    if not token_ad:
        return RedirectResponse(url="/Auth/login")
    if token_ad in BLACKLIST:
        raise HTTPException(status_code=401)
    response = templates.TemplateResponse(
        "Admin_Dashboard.html",
        {"request": request}
    )

    # 🔥 منع الكاش
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response