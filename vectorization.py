import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss 


model_name = "sergeyzh/rubert-tiny-turbo"
model = SentenceTransformer(model_name)

dimension = model.get_sentence_embedding_dimension()

conn = sqlite3.connect("DB_game_information")
cursor = conn.cursor()
cursor.execute("SELECT id, text FROM chunks")
rows = cursor.fetchall()
conn.close()

chunk_ids = [row[0] for row in rows]
chunk_texts = [row[1] for row in rows]

embeddings = model.encode(
    chunk_texts,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True
)

M = 32 
base_index = faiss.IndexHNSWFlat(dimension, M)
base_index.hnsw.efConstruction = 200
index = faiss.IndexIDMap2(base_index)

index.add_with_ids(embeddings.astype('float32'), np.array(chunk_ids).astype('int64'))

faiss.write_index(index, "chunks.index")
print("Индекс сохранён в chunks.index")
