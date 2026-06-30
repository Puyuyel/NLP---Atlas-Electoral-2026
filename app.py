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
import traduccion
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
    es_qu = (data.get("lang") or "es").strip().lower() == "qu"
    try:
        # Si el usuario está en quechua, traducimos su pregunta a español para el modelo.
        pregunta_modelo = traduccion.a_espanol(pregunta) if es_qu else pregunta
        res = rag.responder(pregunta_modelo)
        # ...y la respuesta del modelo de vuelta al quechua.
        if es_qu:
            res["answer"] = traduccion.a_quechua(res.get("answer", ""))
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500


@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json(force=True, silent=True) or {}
    pregunta = (data.get("pregunta") or "").strip()
    if not pregunta:
        return jsonify({"error": "Pregunta vacía"}), 400
    historial = data.get("historial") or []
    es_qu = (data.get("lang") or "es").strip().lower() == "qu"

    def sse(ev):
        return f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"

    def generate():
        try:
            if not es_qu:
                # Camino español: streaming normal, token a token.
                for evento in rag.responder_stream(pregunta, historial):
                    yield sse(evento)
                return

            # Camino quechua: traducir entrada (y el historial) al español para el
            # modelo, y la respuesta final al quechua. No se hace streaming de tokens
            # porque la traducción se aplica sobre el texto completo.
            yield sse({"status": "Maskaspa…"})  # "Buscando…"
            pregunta_es = traduccion.a_espanol(pregunta)
            historial_es = [{"role": m.get("role", ""),
                             "content": traduccion.a_espanol(m.get("content", ""))}
                            for m in historial]

            answer_es, fuentes, candidato = "", [], None
            for ev in rag.responder_stream(pregunta_es, historial_es):
                if ev.get("error"):
                    yield sse(ev)
                    return
                if ev.get("done"):
                    answer_es = ev.get("answer", "")
                    fuentes = ev.get("fuentes", [])
                    candidato = ev.get("candidato")
                # Los eventos de status/token intermedios se omiten en quechua.

            yield sse({"status": "Qhichwaman tikrachispa…"})  # "Traduciendo al quechua…"
            answer_qu = traduccion.a_quechua(answer_es)
            yield sse({"done": True, "answer": answer_qu,
                       "fuentes": fuentes, "candidato": candidato})
        except Exception as e:
            yield sse({"error": f"{type(e).__name__}: {e}"})

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
