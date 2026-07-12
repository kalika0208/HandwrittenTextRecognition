import sqlite3
from datetime import datetime

DB_FILE = "ocr_history.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ocr_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT, extracted_text TEXT,
            confidence REAL, created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_result(filename, extracted_text, confidence):
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        "INSERT INTO ocr_history (filename, extracted_text, confidence, created_at) VALUES (?, ?, ?, ?)",
        (filename, extracted_text, confidence, datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()
    conn.close()


def get_all_history():
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT filename, confidence, created_at FROM ocr_history ORDER BY id DESC").fetchall()
    conn.close()
    return rows