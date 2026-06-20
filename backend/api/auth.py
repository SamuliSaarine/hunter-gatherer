import logging
import os
from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

auth_router = APIRouter(prefix="/auth")
logger = logging.getLogger(__name__)


def _secret() -> str:
    return os.environ.get("GAME_SECRET", "")


def _is_authed(game_session: str | None) -> bool:
    s = _secret()
    return bool(s and game_session == s)


def require_auth(game_session: str | None = Cookie(default=None)) -> None:
    if not _is_authed(game_session):
        raise HTTPException(status_code=401, detail="Not authenticated")


class LoginRequest(BaseModel):
    password: str


@auth_router.post("/login")
async def login(request: LoginRequest, response: Response) -> dict:
    s = _secret()
    logger.warning("LOGIN attempt — GAME_SECRET configured: %s", bool(s))
    if not s:
        logger.error("GAME_SECRET is not set")
        raise HTTPException(status_code=500, detail="GAME_SECRET not configured on server")
    if request.password != s:
        logger.warning("LOGIN failed — password mismatch (got %d chars, expected %d chars)", len(request.password), len(s))
        raise HTTPException(status_code=401, detail="Wrong password")
    logger.warning("LOGIN success")
    response.set_cookie(
        key="game_session",
        value=s,
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
