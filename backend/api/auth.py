import os
from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

auth_router = APIRouter(prefix="/auth")

_SECRET = os.environ.get("GAME_SECRET", "")


def _is_authed(game_session: str | None) -> bool:
    return bool(_SECRET and game_session == _SECRET)


def require_auth(game_session: str | None = Cookie(default=None)) -> None:
    if not _is_authed(game_session):
        raise HTTPException(status_code=401, detail="Not authenticated")


class LoginRequest(BaseModel):
    password: str


@auth_router.post("/login")
async def login(request: LoginRequest, response: Response) -> dict:
    if not _SECRET or request.password != _SECRET:
        raise HTTPException(status_code=401, detail="Wrong password")
    response.set_cookie(
        key="game_session",
        value=_SECRET,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=60 * 60 * 24 * 30,
    )
    return {"ok": True}


@auth_router.post("/logout")
async def logout(response: Response) -> dict:
    response.delete_cookie("game_session")
    return {"ok": True}


@auth_router.get("/check")
async def check(game_session: str | None = Cookie(default=None)) -> dict:
    return {"authenticated": _is_authed(game_session)}
