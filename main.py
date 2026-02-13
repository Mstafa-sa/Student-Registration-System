from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from router.user import router as user_router
from  router.dashboard import router as dashboard_router
from router.schedule import  router as schedule_router
from router.courses import router as course_router
from router.Log_out import router as Log_out
from router.Admin_Dashboard import router as Admin_Dashboard
from router.manage_students import router as manage_students
from router.manage_courses_sections import router as manage_courses_sections
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
app.include_router(schedule_router, prefix="/STU", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(course_router, prefix="/STU", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(Log_out, prefix="/STU", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(Admin_Dashboard, prefix="/ADM", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(manage_students, prefix="/ADM", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(manage_courses_sections, prefix="/ADM", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)