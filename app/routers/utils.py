from typing import Union
from fastapi import Header, HTTPException
from app.services.auth import decode_jwt

async def verify_authorization_header(authorization: str | None = Header(None)) -> dict[str, Union[int, dict]]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No authorization header")
    token = authorization.split("Bearer ", 1)[1].strip()
    return decode_jwt(token)

async def get_user_id(authorization: str | None = Header(None)) -> str:
    auth = await verify_authorization_header(authorization)
    try:
        return str(auth["user_id"])
    except KeyError:
        raise HTTPException(status_code=401, detail="Invalid token")
