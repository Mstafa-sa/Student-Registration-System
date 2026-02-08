from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import mysql.connector
import jwt
import datetime
from jinja2.nodes import If
from fastapi.responses import RedirectResponse


router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@router.post("/login", response_class=HTMLResponse)
async def register(request: Request,email: str=Form(...),password: str=Form(...)):
    conn = mysql.connector.connect(host="localhost",user="root",password="Admin@123",database="school")
    cursor = conn.cursor()
    sql = "SELECT * FROM user WHERE email = %s AND password = %s"
    cursor.execute(sql, (email, password))

    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user :
        secret_key = "132"
        Token = jwt.encode({ "id":user[0],"email":user[2]},secret_key,algorithm="HS256")
        response = RedirectResponse(url="/STU/dashboard", status_code=303)
        response.set_cookie(key="token", value=Token, httponly=True)  # httponly لتحسين الأمان
        return response


    return templates.TemplateResponse("login.html", {"request": request })
@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


