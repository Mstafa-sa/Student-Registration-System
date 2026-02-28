from fastapi import Cookie, HTTPException
from jose import jwt, JWTError
from blacklist import BLACKLIST
from dotenv import load_dotenv
import os

load_dotenv()

secret_key = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"


def get_current_user(token: str = Cookie(None)):

     #  التحقق من وجود التوكن 1
     if not token:
         raise HTTPException(status_code=401, detail="Not authenticated")

     # 2 التحقق من الـ blacklist
     if token in BLACKLIST:
         raise HTTPException(status_code=401, detail="Token blacklisted")

     try:
         # 3 فك التوكن
         payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])

         email = payload.get("email")
         role = payload.get("role")
         specialization = payload.get("Specialization")  # قد تكون None

         if not email or not role:
             raise HTTPException(status_code=401, detail="Invalid token payload")

         return {
             "email": email,
             "role": role,
             "Specialization": specialization
        }

     except JWTError:
         raise HTTPException(status_code=401, detail="Invalid or expired token")


