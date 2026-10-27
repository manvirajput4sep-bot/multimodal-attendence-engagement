import sqlite3, json
from pathlib import Path

def init_db(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, class_name TEXT,
            source_name TEXT, duration_seconds INTEGER, people_detected INTEGER,
            engagement_proxy INTEGER, suggestions TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, detection_id TEXT,
            first_seen_seconds REAL, last_seen_seconds REAL, detected_sample_seconds REAL,
            status TEXT, FOREIGN KEY(session_id) REFERENCES sessions(id))""")

def save_session(path, result, attendance_rows):
    with sqlite3.connect(path) as con:
        cur = con.execute("""INSERT INTO sessions
            (created_at,class_name,source_name,duration_seconds,people_detected,engagement_proxy,suggestions)
            VALUES (?,?,?,?,?,?,?)""",
            (result["created_at"],result["class_name"],result["source_name"],result["duration_seconds"],
             result["people_detected"],result["engagement_proxy"],json.dumps(result["suggestions"])))
        sid = cur.lastrowid
        for row in attendance_rows:
            con.execute("""INSERT INTO attendance
                (session_id,detection_id,first_seen_seconds,last_seen_seconds,detected_sample_seconds,status)
                VALUES (?,?,?,?,?,?)""",
                (sid,row["detection_id"],row["first_seen_seconds"],row["last_seen_seconds"],
                 row["detected_sample_seconds"],row["status"]))

def load_sessions(path):
    with sqlite3.connect(path) as con:
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute("SELECT * FROM sessions ORDER BY id DESC")]
    for r in rows:
        r["suggestions"] = json.loads(r["suggestions"])
    return rows

def load_attendance(path):
    with sqlite3.connect(path) as con:
        con.row_factory = sqlite3.Row
        return [dict(r) for r in con.execute("SELECT * FROM attendance ORDER BY id DESC")]
