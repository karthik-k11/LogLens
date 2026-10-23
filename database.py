import sqlite3
import json
from pathlib import Path


DATABASE = str(Path(__file__).resolve().parent / "loglens.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                info_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                debug_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_logs (
                analysis_id INTEGER PRIMARY KEY,
                logs_json TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analysis_history(id)
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def save_analysis(filename, counts, logs=None):
    if not filename:
        filename = "unknown.log"

    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            INSERT INTO analysis_history
            (filename, info_count, warning_count, error_count, debug_count)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                filename,
                int(counts.get("INFO", 0)),
                int(counts.get("WARNING", 0)),
                int(counts.get("ERROR", 0)),
                int(counts.get("DEBUG", 0)),
            ),
        )
        analysis_id = cursor.lastrowid
        connection.execute(
            "INSERT INTO analysis_logs (analysis_id, logs_json) VALUES (?, ?)",
            (analysis_id, json.dumps(logs or [])),
        )
        connection.commit()
        return analysis_id
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_logs(analysis_id):
    if analysis_id is None:
        return []

    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT logs_json FROM analysis_logs WHERE analysis_id = ?",
            (analysis_id,),
        ).fetchone()
        return json.loads(row["logs_json"]) if row else []
    finally:
        connection.close()


def get_history(limit=10):
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT *
            FROM analysis_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    for record in get_history():
        print(record)