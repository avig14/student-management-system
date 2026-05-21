import sqlite3
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "students.db")


class DatabaseHandler:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._conn = None
        if db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_conn(self):
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                course TEXT NOT NULL,
                marks_s1 REAL NOT NULL,
                marks_s2 REAL NOT NULL,
                marks_s3 REAL NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                hashed_password TEXT NOT NULL
            )
        """)
        conn.commit()

    def insert_student(self, student_id, name, age, course, marks, email):
        conn = self._get_conn()
        conn.execute(
            """
            INSERT INTO students (student_id, name, age, course, marks_s1, marks_s2, marks_s3, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (student_id, name, age, course, marks[0], marks[1], marks[2], email),
        )
        conn.commit()

    def fetch_all(self) -> list:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM students ORDER BY name").fetchall()
        return [dict(row) for row in rows]

    def fetch_by_id(self, student_id: str) -> Optional[dict]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        return dict(row) if row else None

    def update_student(self, student_id: str, fields: dict):
        allowed = {"name", "age", "course", "marks_s1", "marks_s2", "marks_s3", "email"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [student_id]
        conn = self._get_conn()
        conn.execute(
            f"UPDATE students SET {set_clause} WHERE student_id = ?", values
        )
        conn.commit()

    def delete_student(self, student_id: str) -> bool:
        conn = self._get_conn()
        cursor = conn.execute(
            "DELETE FROM students WHERE student_id = ?", (student_id,)
        )
        conn.commit()
        return cursor.rowcount > 0

    def search_students(self, query: str, field: str) -> list:
        field_map = {
            "name": "name",
            "id": "student_id",
            "course": "course",
        }
        col = field_map.get(field, "name")
        conn = self._get_conn()
        rows = conn.execute(
            f"SELECT * FROM students WHERE {col} LIKE ?", (f"%{query}%",)
        ).fetchall()
        return [dict(row) for row in rows]

    def insert_user(self, username: str, hashed_password: str):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO users (username, hashed_password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()

    def fetch_user(self, username: str) -> Optional[dict]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None
