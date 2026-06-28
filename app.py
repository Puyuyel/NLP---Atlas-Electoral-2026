"""
Interfaz web del chatbot electoral.
Levanta un servidor Flask que sirve la UI desde templates/ y static/.

Uso:  python app.py   ->  abre http://127.0.0.1:5000
"""
import json
import sys
import io

from flask import Flask, request, jsonify, Response, stream_with_context, render_template

import config
from rag import RAG

app = Flask(__name__)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

print("Cargando modelos locales (la 1ª vez descarga pesos, puede tardar)...")
rag = RAG()
print("Listo. Abre http://127.0.0.1:5000 en tu navegador.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/meta")
def meta():
    return jsonify({
        "candidatos": [c["nombre"] for c in config.CANDIDATOS],
        "planos": rag.planos_disponibles(),
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    pregunta = (data.get("pregunta") or "").strip()
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400
    try:
        return jsonify(rag.responder(pregunta))
    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json(force=True, silent=True) or {}
    pregunta = (data.get("pregunta") or "").strip()
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400
    historial = data.get("historial") or []

    def generate():
        try:
            for evento in rag.responder_stream(pregunta, historial):
                yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'{type(e).__name__}: {e}'}, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
