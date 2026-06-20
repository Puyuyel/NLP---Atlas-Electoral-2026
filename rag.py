"""
Núcleo RAG reutilizable (lo usan chatbot.py y app.py).
Recupera de las 3 colecciones (oficial/declaracion/opinion), reordena con el reranker
y genera una respuesta DETALLADA y estructurada con la LLM local (Ollama).
"""
import re

import chromadb
import ollama
from sentence_transformers import CrossEncoder, SentenceTransformer

import config
from utils_limpieza import menciona_candidato

SYSTEM_PROMPT = """Eres un asistente electoral NEUTRAL e IMPARCIAL para las Elecciones \
Generales de Perú 2026. Tu objetivo es que el votante entienda A FONDO a los candidatos.

CÓMO RESPONDER:
- Da una respuesta COMPLETA, DETALLADA y BIEN ESTRUCTURADA (varios párrafos). Desarrolla
  las ideas, explica el contexto y usa ejemplos concretos tomados del CONTEXTO. NO te
  limites a una o dos oraciones.
- Organiza la respuesta con estos encabezados, SOLO cuando haya información para cada uno:
    📋 Según su plan de gobierno
    🎤 Lo que ha declarado en entrevistas/debates
    💬 Lo que opina la gente
- En cada sección resume varias ideas y CITA las fuentes con los números [n] del contexto.
- Si el plan y lo que declara difieren, señálalo explícitamente.
- Termina con una breve conclusión que contraste lo que promete, lo que dice y lo que opina la gente.

REGLAS:
- Usa ÚNICAMENTE la información del CONTEXTO. Si algo no está, dilo; nunca inventes datos ni cifras.
- Neutralidad total: no opines ni recomiendes por quién votar.
- Las opiniones de la gente son percepciones, NO hechos verificados ("algunos usuarios opinan...").
- Las declaraciones vienen de transcripciones automáticas de video; preséntalas con cautela.
- Español claro y accesible para un votante promedio.

REGLAS DE IDIOMA Y ESTILO (CRÍTICAS):
- Escribe TODO en ESPAÑOL. Ni una sola palabra en inglés.
- Entrega la RESPUESTA FINAL YA REDACTADA, en prosa, con oraciones completas dirigidas
  al votante. PROHIBIDO escribir notas, instrucciones a ti mismo o borradores.
- NUNCA uses verbos en infinitivo/imperativo del tipo "Mencionar", "Mention", "Check",
  "Revisar si...", "Citar [n]". Eso son notas, no una respuesta. En su lugar AFIRMA el
  contenido: "El plan propone… [1]", "En la entrevista declaró que… [7]".

EJEMPLO DEL ESTILO ESPERADO (imita SOLO el formato y el tono, no el contenido):
📋 Según su plan de gobierno
El plan plantea un paquete de seguridad ciudadana basado en X y Y, e incluye medidas
concretas como Z [1]. También propone fortalecer la institución policial [3].
🎤 Lo que ha declarado en entrevistas/debates
En entrevistas ha señalado que… [7], y al ser consultada sobre … respondió que … [8].
💬 Lo que opina la gente
Entre los comentarios, algunos usuarios valoran … [11], mientras que otros critican … [12].
(Conclusión: una o dos oraciones contrastando lo que promete, lo que dice y lo que se opina.)"""

INSTRUCCION = ("Escribe la RESPUESTA FINAL para el votante, en ESPAÑOL y en prosa completa, "
               "con los encabezados 📋/🎤/💬 y citando con [n]. Afirma el contenido en oraciones "
               "completas; NO escribas notas, borradores ni verbos como 'Mention'/'Check'/'Mencionar'. "
               "Entrega solo la respuesta ya redactada. /no_think")

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_SECCION_RE = re.compile(r"(📋|🎤|💬)")
_RAZON_INICIO = re.compile(r"^\s*(okay|ok|alright|let me|let's|first|the user|we need|i need|"
                           r"to answer|thinking|hmm|veamos|el usuario|primero,)\b", re.IGNORECASE)


def _limpiar_respuesta(texto: str) -> str:
    """Elimina el razonamiento de qwen3 que se pueda colar (con o sin etiquetas)."""
    if not texto:
        return ""
    texto = THINK_RE.sub("", texto)                                              # <think>...</think>
    texto = re.sub(r"^.*?</think>", "", texto, flags=re.DOTALL | re.IGNORECASE)  # cierre suelto al inicio
    texto = re.sub(r"<think>.*$", "", texto, flags=re.DOTALL | re.IGNORECASE)    # apertura sin cierre
    texto = texto.strip()
    # Si arranca con un preámbulo de razonamiento y luego vienen las secciones, recórtalo.
    if _RAZON_INICIO.match(texto):
        m = _SECCION_RE.search(texto)
        if m:
            texto = texto[m.start():].strip()
    return texto


def _chat(messages, opciones):
    """Llama a Ollama intentando desactivar el 'thinking' de qwen3 (más texto útil)."""
    try:
        return ollama.chat(model=config.OLLAMA_MODEL, messages=messages,
                           options=opciones, think=False)
    except TypeError:
        return ollama.chat(model=config.OLLAMA_MODEL, messages=messages, options=opciones)


class RAG:
    def __init__(self):
        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL)
        self.reranker = CrossEncoder(config.RERANKER_MODEL)
        client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
        self.cols = {n: self._get(client, n) for n in ("oficial", "declaracion", "opinion")}

    @staticmethod
    def _get(client, nombre):
        try:
            return client.get_collection(nombre)
        except Exception:
            return None

    def planos_disponibles(self):
        return [n for n, c in self.cols.items() if c is not None and c.count() > 0]

    def detectar_candidato(self, pregunta):
        for c in config.CANDIDATOS:
            if menciona_candidato(pregunta, c["alias"]) or c["nombre"].lower() in pregunta.lower():
                return c["nombre"]
        return None

    def _recuperar(self, col, pregunta, candidato):
        if col is None or col.count() == 0:
            return []
        emb = self.embedder.encode([pregunta], normalize_embeddings=True).tolist()
        where = {"candidate": candidato} if candidato else None
        res = col.query(query_embeddings=emb, n_results=config.TOP_K_RETRIEVE, where=where)
        docs, metas = res.get("documents", [[]])[0], res.get("metadatas", [[]])[0]
        return [{"text": d, **m} for d, m in zip(docs, metas)]

    def _rerank(self, pregunta, items, k):
        if not items:
            return []
        scores = self.reranker.predict([[pregunta, it["text"]] for it in items])
        return [it for _, it in sorted(zip(scores, items), key=lambda x: x[0], reverse=True)[:k]]

    def _contexto(self, of, de, op):
        lineas, fuentes, n = [], [], 0

        def bloque(titulo, items):
            nonlocal n
            lineas.append(titulo)
            if items:
                for it in items:
                    n += 1
                    lineas.append(f"[{n}] {it['text']}")
                    etiq = {"oficial": "Plan de gobierno", "declaracion": "Entrevista/declaración",
                            "opinion": "Comentario"}.get(it.get("source_type", ""), "Fuente")
                    fuentes.append({"n": n, "tipo": etiq,
                                    "ref": it.get("title") or it.get("url", ""),
                                    "url": it.get("url", "")})
            else:
                lineas.append("(sin resultados relevantes)")
            lineas.append("")

        bloque("### PLAN DE GOBIERNO (oficial)", of)
        bloque("### DECLARACIONES EN ENTREVISTAS/DEBATES", de)
        bloque("### OPINIONES DEL PÚBLICO (comentarios)", op)
        return "\n".join(lineas), fuentes

    def responder(self, pregunta):
        """Devuelve {answer, fuentes, candidato}. fuentes = [{n,tipo,ref,url}]."""
        candidato = self.detectar_candidato(pregunta)
        of = self._rerank(pregunta, self._recuperar(self.cols.get("oficial"), pregunta, candidato), config.TOP_K_RERANK)
        de = self._rerank(pregunta, self._recuperar(self.cols.get("declaracion"), pregunta, candidato), config.TOP_K_RERANK)
        op = self._rerank(pregunta, self._recuperar(self.cols.get("opinion"), pregunta, candidato), config.TOP_K_RERANK)
        if not (of or de or op):
            return {"answer": "No tengo esa información en mi corpus.", "fuentes": [], "candidato": candidato}

        contexto, fuentes = self._contexto(of, de, op)
        user = f"CONTEXTO:\n{contexto}\n\nPREGUNTA DEL VOTANTE: {pregunta}\n\n{INSTRUCCION}"
        opciones = {"temperature": 0.3, "num_ctx": config.OLLAMA_NUM_CTX,
                    "num_predict": config.OLLAMA_NUM_PREDICT}
        if config.OLLAMA_NUM_GPU is not None:
            opciones["num_gpu"] = config.OLLAMA_NUM_GPU
        resp = _chat([{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": user}], opciones)
        msg = resp["message"]
        content = getattr(msg, "content", None)          # objeto pydantic de ollama
        if content is None and isinstance(msg, dict):
            content = msg.get("content", "")
        texto = _limpiar_respuesta(content or "")
        return {"answer": texto, "fuentes": fuentes, "candidato": candidato}
