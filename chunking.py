import sqlite3
from datetime import datetime


SIZE_CHANK = 300
OVERLAP = 100 
DB_PATH = "DB_game_information"


def split_into_chanks(text):
    
    words = text.split()
    total = len(words)

    if (total<=SIZE_CHANK):
        return [text]
    
    chunks = []
    step = SIZE_CHANK-OVERLAP

    start = 0
    while start<total:
        end = min(start + SIZE_CHANK, total)
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        if end == total:
            break
        
        start += step

    return chunks


def main():
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM game_information")


    cursor.execute("SELECT rowid,text FROM game_information ORDER BY rowid")

    games = cursor.fetchall()

    cursor.execute("DELETE FROM chunks")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='chunks'")
    conn.commit()


    chunks=[]
    for game_id, text in games:
        chunks = split_into_chanks(text)
        cursor.executemany(
            "INSERT INTO chunks (game_id, chunk_index, text) VALUES (?, ?, ?)",
            [(game_id, i, chunk) for i, chunk in enumerate(chunks)]
            )
        conn.commit()


if __name__ == "__main__":
    main()

