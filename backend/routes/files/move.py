from fastapi import APIRouter, HTTPException, status, Depends, Form
from backend.routes.auth.utils import get_current_user
from backend.db.connect_db import get_db_connection
from .utils import get_or_create_folder

router = APIRouter()

@router.post("/{file_id}/move")
def move_file(
    file_id: int,
    target_folder_id: int | None = Form(None),
    target_folder_name: str = Form(''),
    current_user: dict = Depends(get_current_user),
):
    """Move a file to another folder. Provide either target_folder_id or target_folder_name."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        row = cur.execute("SELECT id, owner_id, stored_name FROM files WHERE id = ?", (file_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        if row['owner_id'] != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu do pliku.")

        resolved_folder_id = None
        folder_name = ''
        if target_folder_id is not None:
            f = cur.execute("SELECT id, name FROM folders WHERE id = ? AND owner_id = ?", (target_folder_id, current_user['id'])).fetchone()
            if not f:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid target_folder_id")
            resolved_folder_id = target_folder_id
            folder_name = f['name']
        elif target_folder_name:
            resolved_folder_id = get_or_create_folder(conn, current_user['id'], target_folder_name)
            folder_name = target_folder_name
        # else: move to root (NULL, '')

        # Poprawka: aktualizuj oba pola — folder_id (int) i folder (text) — dla spójności
        cur.execute("UPDATE files SET folder_id = ?, folder = ? WHERE id = ?", (resolved_folder_id, folder_name, file_id))
        conn.commit()
        return {"moved": True, "file_id": file_id, "folder_id": resolved_folder_id}
    finally:
        conn.close()