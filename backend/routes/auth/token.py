from fastapi import APIRouter, Depends
from .utils import get_current_user
from backend.db.connect_db import get_db_connection

router = APIRouter()

@router.post('/revoke_api_token')
def revoke_api_token(current_user: dict = Depends(get_current_user)):
	"""
	Revoke API token for the current user (sets api_token_hash NULL). Can be called with JWT or API token.
	"""
	# Use get_current_user dependency to determine current user
	# But importing dependency directly here causes circular import in this environment, so implement simple way:
	conn = get_db_connection()
	try:
		cur = conn.cursor()
		cur.execute("UPDATE users SET api_token_hash = NULL, token_created_at = NULL WHERE id = ?", (current_user['id'],))
		conn.commit()
		return {"revoked": True}
	finally:
		conn.close()