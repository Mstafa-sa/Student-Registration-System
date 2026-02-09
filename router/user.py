
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
import mysql.connector
import jwt
import datetime
from jinja2.nodes import If
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext


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
        Token = jwt.encode({ "email":user[2]},secret_key,algorithm="HS256")
        response = RedirectResponse(url="/STU/dashboard", status_code=303)
        response.set_cookie(key="token", value=Token, httponly=True)  # httponly لتحسين الأمان
        return response


    return templates.TemplateResponse("login.html", {"request": request ,"message":"Incorrect username or password"})
@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup", response_class=HTMLResponse)
async def signup(request: Request,name: str=Form(...),email: str=Form(...),password: str=Form(...), check_password:str=Form(...),Specialization:str=Form(...)):
    con=mysql.connector.connect(host="localhost",user="root",password="Admin@123",database="school")
    secret_key="132"
    cursor = con.cursor()
    sql="insert into user (full_name,email,password,Specialization) values (%s,%s,%s,%s)"
    if password == check_password:

        print("password:", password)
        print("length:", len(password))
        print("bytes:", len(password.encode()))

        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        hash=pwd_context.hash(password)

        print(hash)
        token=jwt.encode({"email":email},secret_key,algorithm="HS256")
        cursor.execute(sql,(name,email,hash,Specialization))
        con.commit()
        cursor.close()
        con.close()
        response=RedirectResponse("/STU/dashboard", status_code=303)
        response.set_cookie(key="token", value=token, httponly=True)
        return response
    return templates.TemplateResponse("signup.html", {"request": request,"message":"Incorrect username or password"})