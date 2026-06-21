import datetime

import jwt
from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel

from core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и авторизация"],
)


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
async def login(data: LoginRequest, response: Response):
    if data.password == settings.CORRECT_PASSWORD:
        expire = datetime.datetime.now() + datetime.timedelta(
            minutes=settings.SESSION_TIMEOUT_MINUTES
        )

        payload = {"sub": "admin", "exp": expire}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

        response.set_cookie(
            key="auth_token",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=settings.SESSION_TIMEOUT_MINUTES * 60,
        )

        return {"success": True}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный пароль"
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="auth_token", httponly=True, samesite="lax")
    return {"success": True}


@router.get("/check-auth")
async def check_auth(request: Request, response: Response):
    token = request.cookies.get("auth_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизован"
        )

    try:
        jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return {"isAuthenticated": True}
    except jwt.ExpiredSignatureError:
        response.delete_cookie(key="auth_token", httponly=True, samesite="lax")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия истекла"
        )
    except jwt.InvalidTokenError:
        response.delete_cookie(key="auth_token", httponly=True, samesite="lax")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен"
        )
