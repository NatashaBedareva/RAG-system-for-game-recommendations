import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss 
from transformers import pipeline
import torch

model = SentenceTransformer("sergeyzh/rubert-tiny-turbo")
index = faiss.read_index("chunks.index")
if torch.cuda.is_available():
    device = "cuda" 
else:
    device = "cpu"
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct", device_map=device)

def start_model():
    pass

def search_chunks(question_text, N=5):

    query_vector = model.encode(
        [question_text],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype('float32')

    distances, found_ids = index.search(query_vector, N)
    ids_list = found_ids[0].tolist()

    ids_list = [i for i in ids_list if i != -1]
    if not ids_list:
        return []

    conn = sqlite3.connect("DB_game_information")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(ids_list))

    cursor.execute(f"""
        SELECT c.id, c.text, c.game_id, g.title, g.url
        FROM chunks c
        JOIN game_information g ON g.rowid = c.game_id
        WHERE c.id IN ({placeholders})
    """, ids_list)
    rows = cursor.fetchall()
    conn.close()

    by_id = {row["id"]: dict(row) for row in rows}

    results = []
    for rank, chunk_id in enumerate(ids_list):
        if chunk_id in by_id:
            item = by_id[chunk_id]
            item["score"] = float(distances[0][rank])  # косинусное сходство
            results.append(item)

    return results


def answer_model(question_text):
    chunks = search_chunks(question_text, N=3)

    context = ""
    for r in chunks:
        context += f"{r['title']} \n URL: {r['url']} \n {r['text']}\n"

    
    prompt = f'''Контекст: {context}
    Исходя из контекста, ответьте на следующий вопрос:
    Вопрос: {question_text}
    Предоставь ответ только на основе предоставленного контекста, без использования общих знаний. Ответ должен быть непосредственно взят из предоставленного контекста.
    Если в контексте нет информации, достаточной для ответа на вопрос, укажите, что доступных данных недостаточно для ответа.
    '''
        
    messages = [{"role": "user", "content": prompt}]

    output  = pipe(messages, max_new_tokens=512)
    answer_text = output [0]['generated_text'][-1]['content']
    sources = [
        {"title": r["title"], "url": r["url"], "score": r["score"]}
        for r in chunks
    ]
    return answer_text,sources
    