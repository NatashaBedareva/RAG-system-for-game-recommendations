from parser import run_parser
from db import close_db,start_db,commit_db

try:
    start_db()
    run_parser()
except Exception as e:
    print(f"Парсер упал: {type(e).__name__}: {e}")
finally:
    commit_db()
    close_db()