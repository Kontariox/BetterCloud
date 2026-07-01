from fastapi import APIRouter, HTTPException, status, Depends
import sqlite3
from datetime import datetime, timezone, timedelta
from backend.routes.auth.schemas import RegisterRequest
from .utils import get_password_hash, create_access_token
from backend.db.connect_db import get_db_connection


router = APIRouter()

@router.post('/register')
def register(req: RegisterRequest):
	conn = get_db_connection()
	try:
		cur = conn.cursor()
		pw_hash = get_password_hash(req.password)
		now = datetime.now(timezone.utc).isoformat()
		try:
			cur.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)", (req.username, pw_hash, now))
			conn.commit()
			print("dodaje")
		except sqlite3.IntegrityError as e:
			print("SQL ERROR:", e)
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=str(e)
			)
		cur.execute("SELECT id, username FROM users WHERE username = ?", (req.username,))
		row = cur.fetchone()
		user_id = row['id']
		token = create_access_token({"sub": str(user_id), "username": req.username}, expires_delta=timedelta(days=7))
		return {"access_token": token, "token_type": "bearer"}
	finally:
		conn.close()