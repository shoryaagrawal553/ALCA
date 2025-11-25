import sqlite3
import json
from datetime import datetime


class MemoryManager:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._create_tables()

    # ---------------------------------------------
    # INTERNAL UTILITIES
    # ---------------------------------------------
    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        conn = self._connect()
        cur = conn.cursor()

        # Stores accuracy, attempts, wins/losses per topic
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id TEXT,
                topic TEXT,
                attempts INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, topic)
            )
        """)

        # Stores each answer for detailed analytics
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                topic TEXT,
                question_id TEXT,
                correct INTEGER,
                student_answer TEXT,
                correct_answer TEXT,
                timestamp TEXT
            )
        """)

        conn.commit()
        conn.close()

    # ---------------------------------------------
    # MEMORY WRITE OPERATIONS
    # ---------------------------------------------
    def record_attempt(self, user_id, topic, question_id, student_answer, correct_answer, is_correct):
        conn = self._connect()
        cur = conn.cursor()

        # 1. Update cumulative stats
        cur.execute("""
            INSERT INTO user_stats (user_id, topic, attempts, correct)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, topic)
            DO UPDATE SET 
                attempts = attempts + 1,
                correct = correct + excluded.correct
        """, (user_id, topic, 1 if is_correct else 0))

        # 2. Record full history
        cur.execute("""
            INSERT INTO history (user_id, topic, question_id, correct,
                                 student_answer, correct_answer, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            topic,
            question_id,
            1 if is_correct else 0,
            student_answer,
            correct_answer,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    # ---------------------------------------------
    # MEMORY READ OPERATIONS
    # ---------------------------------------------
    def get_user_topic_stats(self, user_id, topic):
        """Return accuracy & attempts for specific topic."""
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT attempts, correct FROM user_stats
            WHERE user_id = ? AND topic = ?
        """, (user_id, topic))

        row = cur.fetchone()
        conn.close()

        if not row:
            return {"attempts": 0, "correct": 0, "accuracy": 0.0}

        attempts, correct = row
        accuracy = round((correct / attempts) * 100, 2) if attempts > 0 else 0.0
        return {"attempts": attempts, "correct": correct, "accuracy": accuracy}

    def get_user_summary(self, user_id):
        """Return all stats + detailed history."""
        conn = self._connect()
        cur = conn.cursor()

        # Topic-wise stats
        cur.execute("""
            SELECT topic, attempts, correct FROM user_stats
            WHERE user_id = ?
        """, (user_id,))
        stats_rows = cur.fetchall()

        stats = {}
        for topic, attempts, correct in stats_rows:
            accuracy = round((correct / attempts) * 100, 2) if attempts else 0.0
            stats[topic] = {
                "attempts": attempts,
                "correct": correct,
                "accuracy": accuracy
            }

        # Detailed history
        cur.execute("""
            SELECT topic, question_id, correct, student_answer, correct_answer, timestamp
            FROM history WHERE user_id = ?
            ORDER BY timestamp DESC
        """, (user_id,))
        hist_rows = cur.fetchall()

        history = [
            {
                "topic": t,
                "question_id": qid,
                "correct": bool(c),
                "student_answer": sa,
                "correct_answer": ca,
                "timestamp": ts
            }
            for (t, qid, c, sa, ca, ts) in hist_rows
        ]

        conn.close()

        return {
            "user_id": user_id,
            "topics": stats,
            "history": history
        }
