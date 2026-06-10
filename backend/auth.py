from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from backend.database import (
    create_user, get_user_by_username, get_user_by_email, verify_password
)
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY            = os.getenv("SECRET_KEY", "changeme_secret")
ALGORITHM             = "HS256"
TOKEN_EXPIRE_MINUTES  = 60 * 8

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_token(username: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": username, "role": role, "exp": expire},
        SECRET_KEY, algorithm=ALGORITHM
    )


def register_user(username: str, email: str, password: str, role: str):
    if get_user_by_username(username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email already registered")
    create_user(username, email, password, role)
    return {"message": "Registered successfully"}


def login_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {
        "access_token": create_token(username, user["role"]),
        "token_type":   "bearer",
        "role":         user["role"],
        "username":     user["username"],
        "email":        user["email"],
        "user_id":      user["id"]
    }


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str     = payload.get("role", "student")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
