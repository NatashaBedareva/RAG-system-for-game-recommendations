import sqlite3
from datetime import datetime

DB_PATH = "DB_game_information"
TABLE_NAME = "game_information"

_conn = None
_cursor = None


def start_db():
    global _conn, _cursor
    _conn = sqlite3.connect(DB_PATH)
    _cursor = _conn.cursor()
    clear_table()


def clear_table():
    _cursor.execute(f"DELETE FROM {TABLE_NAME}")
    _conn.commit()


def add_data_to_db(game):

    title = game[0]

    _cursor.execute(
        f"SELECT 1 FROM {TABLE_NAME} WHERE title = ? LIMIT 1",
        (title,)
    )
    if _cursor.fetchone() is not None:
        print(f"Пропуск (уже есть): {title}")
        return 

    _cursor.execute(
        f"INSERT INTO {TABLE_NAME} (title, url, text, date) VALUES (?, ?, ?, ?)",
        game
    )
    _conn.commit()
    print(f"Добавлено: {title}")
    return 


def commit_db():
    _conn.commit()


def close_db():
    _conn.close()