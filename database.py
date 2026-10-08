import sqlite3


DATABASE = "loglens.db"


def init_db():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            info_count INTEGER DEFAULT 0,
            warning_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            debug_count INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


def save_analysis(filename, counts):
    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        INSERT INTO analysis_history
        (filename, info_count, warning_count, error_count, debug_count)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            filename,
            counts["INFO"],
            counts["WARNING"],
            counts["ERROR"],
            counts["DEBUG"]
        )
    )

    connection.commit()
    connection.close()


def get_history():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    rows = connection.execute(
        """
        SELECT *
        FROM analysis_history
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()

    history = get_history()

    for record in history:
        print(record)