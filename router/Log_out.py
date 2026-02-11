from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi import Cookie


router = APIRouter()



BLACKLIST = set()

@router.get("/log_out")
async def logout(token: str = Cookie(None)):
    if token:
        BLACKLIST.add(token)  # أضف التوكن إلى القائمة السوداء
    response = RedirectResponse(url="/Auth/login")
    response.delete_cookie(key="token")  # حذف الكوكي من المتصفح
    return response
