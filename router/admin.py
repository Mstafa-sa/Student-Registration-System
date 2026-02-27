from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from auth_utils import get_current_user
from db import  get_db,db_cursor
from fastapi import Depends, HTTPException
load_dotenv()  # ← تقرأ ملف .env

secret_key = os.getenv("JWT_SECRET")


router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")
@router.get("/Registration_time", response_class=HTMLResponse)
async def registration_time(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db)):
    with db_cursor(db) as cursor:
        sql = "select * from major "
        cursor.execute(sql)
        majors = cursor.fetchall()
    with db_cursor(db) as cursor:
        sql = """select * from registration_time reg
              join major  maj on maj.id = reg.id_major"""
        cursor.execute(sql)
        registration = cursor.fetchall()
    return templates.TemplateResponse("admin.html",{"request":request,"majors":majors,"registration":registration})
@router.post("/Registration_time",response_class=HTMLResponse)
async def registration_time(request: Request,user: dict = Depends(get_current_user),db=Depends(get_db),start1:datetime=Form(None),end1:datetime=Form(None),
                            start2:datetime=Form(None),end2:datetime=Form(None),startFinal:datetime=Form(None),delete:str=Form(None),
                            endFinal:datetime=Form(None),major:str=Form(None),action:str=Form(...),major_name:str=Form(None),registration_id:int=Form( None)):
 if action == "add_major":
     with db_cursor(db) as cursor:
         sql = "select id from major where major_name = %s"
         cursor.execute(sql,(major_name,))
         major_id = cursor.fetchone()
     if major_id != None:
         return RedirectResponse(url="/ADM/Registration_time",status_code=302)###########
     with db_cursor(db) as cursor:
         sql = "insert into major (major_name) values (%s)"
         cursor.execute(sql,(major_name,))
     return RedirectResponse(url="/ADM/Registration_time", status_code=302)
 elif action == "delete_major":
     with db_cursor(db) as cursor:
         sql = "delete from major where id = %s"
         cursor.execute(sql,(delete,))
     return RedirectResponse(url="/ADM/Registration_time",status_code=302)
 elif action == "add_time":
     with db_cursor(db) as cursor:
         sql = "select id from registration_time where reg_start1=%s and reg_end1=%s and reg_start2=%s and reg_end2=%s and reg_start3=%s and reg_end3=%s"
         cursor.execute(sql, (start1,end1,start2,end2,startFinal,endFinal))
         time_id = cursor.fetchone()
     if time_id != None:
         return RedirectResponse(url="/ADM/Registration_time",status_code=302)#########
     with db_cursor(db) as cursor:
         sql="insert into registration_time (id_major,reg_start1,reg_end1,reg_start2,reg_end2,reg_start3,reg_end3) values (%s,%s,%s,%s,%s,%s,%s) "
         cursor.execute(sql, (major,start1, end1, start2, end2, startFinal, endFinal))
     return RedirectResponse(url="/ADM/Registration_time",status_code=302)
 elif action == "update_time":
     with db_cursor(db) as cursor:
         sql = "select id from registration_time where reg_start1=%s and reg_end1=%s and reg_start2=%s and reg_end2=%s and reg_start3=%s and reg_end3=%s and id!=%s"
         cursor.execute(sql, (start1, end1, start2, end2, startFinal, endFinal,registration_id))
         time_id = cursor.fetchone()
     if time_id != None:
         return RedirectResponse(url="/ADM/Registration_time", status_code=302)  #########
     with db_cursor(db) as cursor:
         sql="update registration_time set reg_start1=%s,reg_end1=%s,reg_start2=%s,reg_end2=%s,reg_start3=%s,reg_end3=%s  where id_major=%s"
         cursor.execute(sql, (start1, end1, start2, end2, startFinal, endFinal,major))
     return RedirectResponse(url="/ADM/Registration_time",status_code=302)






