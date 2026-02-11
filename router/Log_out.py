from fastapi import APIRouter, Cookie
from fastapi.responses import RedirectResponse

router = APIRouter()

BLACKLIST = set()

@router.get("/log_out")
async def logout(
    token: str = Cookie(None),        # توكن الطالب
    token_ad: str = Cookie(None)      # توكن المدير
):

    response = RedirectResponse(url="/Auth/login", status_code=302)

    # إذا طالب
    if token:
        BLACKLIST.add(token)
        response.delete_cookie("token")

    # إذا مدير
    if token_ad:
        BLACKLIST.add(token_ad)
        response.delete_cookie("token_ad")

    return response
