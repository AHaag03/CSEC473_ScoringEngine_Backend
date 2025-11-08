import sqlite3
from datetime import datetime

DB_PATH = "scores.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS host_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host_name TEXT NOT NULL,
            ip TEXT NOT NULL,
            service_name TEXT NOT NULL,
            success INTEGER NOT NULL,
            points_awarded INTEGER NOT NULL,
            checked_at TEXT NOT NULL,
            message TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS host_scores (
            host_name TEXT PRIMARY KEY,
            total_points INTEGER NOT NULL DEFAULT 0,
            last_updated TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_check(host_name, ip, service_name, success, points, message):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO host_checks (host_name, ip, service_name, success, points_awarded, checked_at, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (host_name, ip, service_name, int(success), points, datetime.utcnow().isoformat(), message))
    conn.commit()
    conn.close()

def upsert_score(host_name, delta_points):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT total_points FROM host_scores WHERE host_name=?", (host_name,))
    row = cur.fetchone()
    if row:
        cur.execute("""
            UPDATE host_scores
            SET total_points = total_points + ?, last_updated=?
            WHERE host_name=?
        """, (delta_points, datetime.utcnow().isoformat(), host_name))
    else:
        cur.execute("""
            INSERT INTO host_scores (host_name, total_points, last_updated)
            VALUES (?, ?, ?)
        """, (host_name, delta_points, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def read_all_scores():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT host_name, total_points FROM host_scores")
    data = cur.fetchall()
    conn.close()
    return {name: pts for name, pts in data}

def read_latest_status_by_host_and_service():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT hc.host_name, hc.service_name, hc.success
        FROM host_checks hc
        INNER JOIN (
            SELECT host_name, service_name, MAX(checked_at) AS max_time
            FROM host_checks
            GROUP BY host_name, service_name
        ) latest
        ON hc.host_name=latest.host_name AND hc.service_name=latest.service_name AND hc.checked_at=latest.max_time
    """)
    rows = cur.fetchall()
    conn.close()
    return {(h, s): bool(ok) for h, s, ok in rows}
