
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import mysql.connector
import jwt
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from dotenv import load_dotenv
import os



load_dotenv()  # ← تقرأ ملف .env

secret_key = os.getenv("JWT_SECRET")


router = APIRouter()

# تعريف templates هنا مباشرة لتجنب circular import
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@router.post("/login", response_class=HTMLResponse)
async def register(request: Request,email: str=Form(...),password: str=Form(...)):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
    cursor = conn.cursor()
    sql = "SELECT * FROM user WHERE email = %s AND password = %s"
    cursor.execute(sql, (email, password))

    user = cursor.fetchone()
    cursor.close()
    conn.close()
    print("user:", user)
    if user :
        print("user:", user[5])
        if user [5] == "student":

         Token = jwt.encode({ "email":user[2],"Specialization":user[4]},secret_key,algorithm="HS256")
         response = RedirectResponse(url="/STU/dashboard", status_code=303)
         response.set_cookie(key="token", value=Token, httponly=True)  # httponly لتحسين الأمان
         return response
        elif user [5] == "Admin":
            Token = jwt.encode({"email": user[2]}, secret_key, algorithm="HS256")
            response = RedirectResponse(url="/ADM/Admin_Dashboard", status_code=303)
            response.set_cookie(key="token_ad", value=Token, httponly=True)  # httponly لتحسين الأمان
            return response

    return templates.TemplateResponse("login.html", {"request": request ,"message":"Incorrect username or password"})
@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup", response_class=HTMLResponse)
async def signup(request: Request,name: str=Form(...),email: str=Form(...),password: str=Form(...), check_password:str=Form(...),Specialization:str=Form(...),hid:str=Form(...)):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
    cursor = con.cursor()
    sql="insert into user (full_name,email,password,Specialization,role) values (%s,%s,%s,%s,%s)"
    if password == check_password:



        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        hash=pwd_context.hash(password)


        token=jwt.encode({"email":email},secret_key,algorithm="HS256")
        cursor.execute(sql,(name,email,hash,Specialization,hid))
        con.commit()
        cursor.close()
        con.close()
        response=RedirectResponse("/STU/dashboard", status_code=303)
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    return templates.TemplateResponse("signup.html", {"request": request,"message":"Incorrect username or password"})