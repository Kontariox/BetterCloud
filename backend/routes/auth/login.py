from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from backend.routes.auth.schemas import LoginRequest
from .utils import create_access_token, verify_password
from backend.db.connect_db import get_db_connection

router = APIRouter()

@router.post('/login')
def login(req: LoginRequest):
	conn = get_db_connection()
	try:
		cur = conn.cursor()
		row = cur.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (req.username,)).fetchone()
		if not row:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
		if not verify_password(req.password, row['password_hash']):
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
		token = create_access_token({"sub": str(row['id']), "username": row['username']}, expires_delta=timedelta(days=7))
		return {"access_token": token, "token_type": "bearer"}
	finally:
		conn.close()