import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "riwayat_emosi.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS riwayat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emosi TEXT NOT NULL,
            waktu TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def simpan_riwayat(emosi: str):
    conn = get_conn()
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO riwayat (emosi, waktu) VALUES (?, ?)", (emosi, waktu))
    conn.commit()
    conn.close()
    return waktu


def ambil_riwayat(limit: int = 200):
    conn = get_conn()
    cur = conn.execute(
        "SELECT emosi, waktu FROM riwayat ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def ambil_terakhir():
    conn = get_conn()
    cur = conn.execute("SELECT emosi, waktu FROM riwayat ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row
