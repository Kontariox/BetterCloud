from fastapi import APIRouter, HTTPException, status, Depends
from backend.routes.auth.utils import get_current_user
from .config import UPLOAD_DIR
from backend.db.connect_db import get_db_connection

router = APIRouter()

@router.delete("/{file_id}")
def delete_file(file_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        row = cur.execute("SELECT id, owner_id, stored_name, name, hash FROM files WHERE id = ?", (file_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        if row['owner_id'] != current_user['id']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu do pliku.")

        # Poprawka: sprawdź referencje PRZED usunięciem rekordu z bazy.
        # Poprzedni kod usuwał rekord najpierw, więc zapytanie zawsze zwracało None.
        other = cur.execute(
            "SELECT id FROM files WHERE (stored_name = ? OR hash = ?) AND id != ?",
            (row['stored_name'], row['hash'], file_id),
        ).fetchone()

        cur.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()

        # Usuń plik fizyczny tylko jeśli żaden inny rekord go nie używa
        if not other:
            if row['stored_name']:
                p = UPLOAD_DIR / row['stored_name']
                if p.exists():
                    p.unlink()

        return {"deleted": True, "file_id": file_id}
    finally:
        conn.close()