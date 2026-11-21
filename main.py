from flask import Flask, request, jsonify, render_template

from search_and_answer import search_chunks, answer_model

app = Flask(__name__)
app.json.ensure_ascii = False

@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Параметр q обязателен"}), 400

    try:
        n = int(request.args.get("n", 5))
    except ValueError:
        return jsonify({"error": "Параметр n должен быть числом"}), 400

    results = search_chunks(q, N=n)

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



@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Пустой вопрос"}), 400

    try:
        answer, sources = answer_model(question)
    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500

    return jsonify({
        "question": question,
        "answer": answer,
        "sources": sources,
    })


if __name__ == "__main__":
    app.run(debug=True)