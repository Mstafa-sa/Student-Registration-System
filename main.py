from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from router.user import router as user_router
from  router.dashboard import router as dashboard_router
app = FastAPI()
# 1️⃣ ربط مجلد static للـ CSS
app.mount("/static", StaticFiles(directory="static"), name="static")



# 3️⃣ إضافة router مع تمرير templates
app.include_router(user_router, prefix="/Auth", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(dashboard_router, prefix="/STU", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
