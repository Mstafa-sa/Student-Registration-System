from fastapi import APIRouter, Cookie
from fastapi.responses import RedirectResponse
router = APIRouter()
from blacklist import BLACKLIST

@router.get("/log_out")
async def logout(
    token: str = Cookie(None),
):
        response = RedirectResponse(url="/Auth/login", status_code=302)
        if token:
            BLACKLIST.add(token)
            response.delete_cookie("token")

        return response