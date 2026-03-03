from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from router.user import router as user_router
from  router.dashboard import router as dashboard_router
from router.schedule import  router as schedule_router
from router.courses import router as course_router
from router.Log_out import router as Log_out
from router.Admin_Dashboard import router as Admin_Dashboard
from router.manage_students import router as manage_students
from router.manage_courses_sections import router as manage_courses_sections
from router.reports import router as reports
from router.courses_available import router as coursesAvailable
from middleware.logging_middleware import LoggingMiddleware
from router.admin import router as admin_router
from router.teacher_dashbord import router as teacher_dashboard_router
from router.teacherCourses import router as teacher_teacherCourses
app = FastAPI()
app.add_middleware(LoggingMiddleware)
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
app.include_router(reports, prefix="/ADM", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(coursesAvailable, prefix="/STU", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(admin_router, prefix="/ADM", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(teacher_dashboard_router, prefix="/TEA", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)
app.include_router(teacher_teacherCourses, prefix="/TEA", tags=["user"],
                   responses={404: {"description": "Not found"}},
                   # هنا نمرر templates كـ dependency
)