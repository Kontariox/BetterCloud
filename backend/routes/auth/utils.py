from fastapi import HTTPException, status, Header
import os
from backend.db.connect_db import get_db_connection
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import hashlib
from dotenv import load_dotenv

load_dotenv()

# JWT settings
# Bezpieczeństwo: SECRET_KEY musi być ustawiony przez zmienną środowiskową JWT_SECRET_KEY.
# Fallback jest tylko dla środowiska deweloperskiego
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change_this_secret_to_something_secure")
if SECRET_KEY == "change_this_secret_to_something_secure":
    import warnings
    warnings.warn(
        "JWT_SECRET_KEY nie jest ustawiony! Używam niebezpiecznego klucza domyślnego. "
        "Ustaw zmienną środowiskową JWT_SECRET_KEY w produkcji.",
        stacklevel=1,
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # RFC requires numeric timestamps for exp/iat
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency to get current user. Accepts:
    - Bearer <JWT> (our JWT tokens)
    - Bearer <opaque_token> (legacy API token) — matches by hash
    Returns dict {id, username}
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format")
    token = parts[1]

    # First try JWT — łapiemy tylko JWTError, nie wszystkie wyjątki
    try:
        payload = decode_access_token(token)
    except JWTError:
        pass
    else:
        user_id = payload.get("sub")
        username = payload.get("username")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        try:
            return {"id": int(user_id), "username": username}
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    # Not a valid JWT — try opaque token lookup (compare hashes)
    token_hash = hash_token(token)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        row = cur.execute("SELECT id, username FROM users WHERE api_token_hash = ?", (token_hash,)).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"id": row["id"], "username": row["username"]}
    finally:
        conn.close()
