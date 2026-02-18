import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    print("DB FILE LOADED")

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="school"
    )
