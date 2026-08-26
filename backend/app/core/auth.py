"""
JWT Authentication + Role-Based Access Control (RBAC).
Day 4 — Person A (Backend/Integration)

Roles:
  OFFICER  — submit decisions, use AI chat, view all bidder dossiers
  ADMIN    — manage users, view audit logs, override decisions
  AUDITOR  — read-only access to audit logs and compliance records (CAG)
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Config — override via environment variables in production
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_USE_A_LONG_RANDOM_STRING")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class TokenData(BaseModel):
    username: str
    role: str
    exp: Optional[datetime] = None


class UserCredentials(BaseModel):
    username: str
    password: str


# ---------------------------------------------------------------------------
# Demo users (Day 1–3 stub; replace with PostgreSQL users table on Day 4)
# ---------------------------------------------------------------------------
DEMO_USERS = {
    "officer.sharma": {
        "hashed_password": pwd_context.hash("officer123"),
        "role": "OFFICER",
        "full_name": "Rajesh Sharma, Senior Procurement Officer",
    },
    "admin.procure": {
        "hashed_password": pwd_context.hash("admin123"),
        "role": "ADMIN",
        "full_name": "Procurement Admin",
    },
    "auditor.cag": {
        "hashed_password": pwd_context.hash("auditor123"),
        "role": "AUDITOR",
        "full_name": "CAG Field Auditor",
    },
}

# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenData(username=payload["sub"], role=payload["role"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> TokenData:
    return decode_token(credentials.credentials)


def require_role(*allowed_roles: str):
    """Returns a FastAPI dependency that enforces role-based access."""
    def _check(user: TokenData = Depends(get_current_user)) -> TokenData:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {allowed_roles}",
            )
        return user
    return _check


# Convenience dependency aliases
require_officer = require_role("OFFICER", "ADMIN")
require_admin   = require_role("ADMIN")
require_auditor = require_role("OFFICER", "ADMIN", "AUDITOR")


# ---------------------------------------------------------------------------
# Login endpoint helper (called from main.py)
# ---------------------------------------------------------------------------
def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = DEMO_USERS.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return {"username": username, **user}
