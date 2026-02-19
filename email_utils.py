import aiosmtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
async def send_email(to_email: str, reset_link: str):
    message = EmailMessage()
    message["From"] = "your_email@gmail.com"
    message["To"] = to_email
    message["Subject"] = "إعادة تعيين كلمة السر"
    message.set_content(f"اضغط على الرابط لتغيير كلمة السر: {reset_link}")

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=465,
        use_tls=True,
        username="pupilsystem@gmail.com",
        password=os.getenv("password"),
        timeout=20
    )

