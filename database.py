import sqlite3
from pathlib import Path


DATABASE = str(Path(__file__).resolve().parent / "loglens.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
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
    connection.commit()
    connection.close()


def save_analysis(filename, counts):
    if not filename:
        filename = "unknown.log"

    connection = get_connection()
    connection.execute(
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
    connection.commit()
    connection.close()


def get_history(limit=10):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT *
        FROM analysis_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    connection.close()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    for record in get_history():
        print(record)