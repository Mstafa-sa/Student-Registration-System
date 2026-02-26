import mysql.connector
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()


#  إنشاء الاتصال بقاعدة البيانات
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )


#  Dependency Injection للـ FastAPI
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
#  Context Manager لإدارة cursor تلقائيًا (الأفضل لك)
@contextmanager
def db_cursor(db):
    cursor = db.cursor(buffered=True)
    try:
        yield cursor
        db.commit()   #  commit تلقائي عند النجاح
    finally:
        cursor.close()  #  إغلاق cursor دائمًا