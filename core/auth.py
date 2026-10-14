import datetime
import os

import jwt
from fastapi import APIRouter, Request, HTTPException, status, Depends, Response
from pwdlib import PasswordHash

from models.auth.login import LoginIn

SECRET = os.environ.get('JWT_SECRET')
ALGO = os.environ.get('JWT_ALGO')
ph = PasswordHash.recommended()
router = APIRouter(prefix="/auth")


USERS = {}

def make_token(email:str, role:str) -> str:
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    return jwt.encode({"sub": email, "role": role, "exp": exp}, SECRET, algorithm=ALGO)

def current_user(request: Request) -> dict:
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

def require_admin(user=Depends(current_user)):
    if user['role'] != 'admin':
        raise HTTPException(403)
    return user

@router.post("/login")
async def login(body: LoginIn, response: Response):
    user = USERS.get(body.email.lower())
    if not user or not ph.verify(body.password, user["hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password.")
    response.set_cookie("session", make_token(body.email.lower(), user['role']), httponly=True, secure=True, samesite="lax", max_age=8 * 3600)
    return {"email": body.email.lower(), "role": user['role']}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("session")
    return {"ok": True}

