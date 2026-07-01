import hashlib
import sqlite3
from datetime import datetime, timezone


def get_or_create_folder(conn, owner_id: int, name: str) -> int:
    cur = conn.cursor()
    row = cur.execute("SELECT id FROM folders WHERE owner_id = ? AND name = ? AND parent_id IS NULL", (owner_id, name)).fetchone()
    if row:
        return row['id'] if isinstance(row, sqlite3.Row) else row[0]
    now = datetime.now(timezone.utc).isoformat()
    cur.execute("INSERT INTO folders (owner_id, name, parent_id, created_at) VALUES (?, ?, ?, ?)", (owner_id, name, None, now))
    conn.commit()
    return cur.lastrowid

def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()