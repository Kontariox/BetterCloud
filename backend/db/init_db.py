from .config import DB_DIR, DB_PATH
import sqlite3

def init_database() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                token TEXT,
                created_at TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                api_token_hash TEXT UNIQUE,
                token_created_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                parent_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES folders (id) ON DELETE SET NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                size TEXT NOT NULL,
                hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                stored_name TEXT,
                folder TEXT DEFAULT '',
                folder_id INTEGER,
                FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (folder_id) REFERENCES folders (id) ON DELETE SET NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                time TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

init_database()