# memory.py
import sqlite3
import json
import time
from typing import Any, Dict, List, Optional

DB_FILE = "memory.db"


# ------------------------------------------------------
# 1. Initialize SQLite database (automatically on import)
# ------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Store key–value memory entries
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_memory (
            user_id TEXT,
            key TEXT,
            value TEXT,
            ts INTEGER,
            PRIMARY KEY (user_id, key)
        )
    ''')

    # Store session history logs
    c.execute('''
        CREATE TABLE IF NOT EXISTS session_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            topic TEXT,
            action TEXT,
            payload TEXT,
            ts INTEGER
        )
    ''')

    conn.commit()
    conn.close()


# ------------------------------------------------------
# 2. Save a memory value
# ------------------------------------------------------
def save_memory(user_id: str, key: str, value: Any):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''
        REPLACE INTO user_memory (user_id, key, value, ts)
        VALUES (?, ?, ?, ?)
    ''', (user_id, key, json.dumps(value), int(time.time())))

    conn.commit()
    conn.close()


# ------------------------------------------------------
# 3. Load a memory value
# ------------------------------------------------------
def load_memory(user_id: str, key: str) -> Optional[Any]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('SELECT value FROM user_memory WHERE user_id=? AND key=?', (user_id, key))
    row = c.fetchone()

    conn.close()

    if row:
        return json.loads(row[0])
    return None


# ------------------------------------------------------
# 4. Add an entry to session history
# ------------------------------------------------------
def append_session(user_id: str, topic: str, action: str, payload: Any):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''
        INSERT INTO session_history (user_id, topic, action, payload, ts)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, topic, action, json.dumps(payload), int(time.time())))

    conn.commit()
    conn.close()


# ------------------------------------------------------
# 5. Retrieve session history
# ------------------------------------------------------
def get_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''
        SELECT id, topic, action, payload, ts
        FROM session_history
        WHERE user_id=?
        ORDER BY ts DESC
        LIMIT ?
    ''', (user_id, limit))

    rows = c.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "topic": r[1],
            "action": r[2],
            "payload": json.loads(r[3]),
            "ts": r[4]
        })

    return result


# Initialize the DB immediately when file is imported
init_db()
