from flask import Flask, request, jsonify
from search_and_answer import search_chunks, answer_model

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Параметр q обязателен"}), 400

    # N — сколько чанков вернуть (по умолчанию 5)
    try:
        n = int(request.args.get("n", 5))
    except ValueError:
        return jsonify({"error": "Параметр n должен быть числом"}), 400

    results = search_chunks(q, N=n)

    # Приводим sqlite3.Row к обычному dict для JSON
    return jsonify([
        {
            "chunk_id": r["id"],
            "game_id": r["game_id"],
            "title": r["title"],
            "url": r["url"],
            "text": r["text"],
            "score": r["score"],
        }
        for r in results
    ])


@app.route("/ask")
def ask():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Параметр q обязателен"}), 400

    # answer_model сейчас печатает ответ и ничего не возвращает.
    # Нужно переделать её, чтобы она возвращала (answer, sources).
    answer, sources = answer_model(q)

    return jsonify({
        "question": q,
        "answer": answer,
        "sources": sources,
    })


if __name__ == "__main__":
    app.run(debug=True)