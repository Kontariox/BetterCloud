from fastapi import APIRouter, Depends
from backend.routes.auth.utils import get_current_user
from backend.db.connect_db import get_db_connection

router = APIRouter()

@router.get("/")
def list_files(
    current_user: dict = Depends(get_current_user),
    folder: str = '',
    folder_id: int | None = None,
    root_only: bool = False,
    search: str = '',
    sort_by: str = 'created_at',
    sort_desc: bool = True
):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        query = "SELECT f.id, f.owner_id, f.name, f.size, f.hash, f.created_at, f.stored_name, f.folder_id, fol.name as folder_name FROM files f LEFT JOIN folders fol ON f.folder_id = fol.id WHERE f.owner_id = ?"
        params = [current_user["id"]]

        if folder_id is not None:
            query += " AND f.folder_id = ?"
            params.append(folder_id)
        elif root_only:
            query += " AND f.folder_id IS NULL"
        elif folder:
            query += " AND fol.name = ?"
            params.append(folder)

        if search:
            query += " AND f.name LIKE ?"
            params.append(f"%{search}%")

        allowed_sorts = {'name': 'f.name', 'size': 'CAST(f.size AS INTEGER)', 'created_at': 'f.created_at'}
        sort_col = allowed_sorts.get(sort_by, 'f.created_at')
        direction = "DESC" if sort_desc else "ASC"

        query += f" ORDER BY {sort_col} {direction}, f.id DESC"

        rows = cur.execute(query, tuple(params)).fetchall()
        result = [dict(row) for row in rows]
    finally:
        conn.close()
    return result