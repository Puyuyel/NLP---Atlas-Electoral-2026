# Chatbot electoral Perú 2026 — RAG local (3 planos)

Chatbot en español que responde sobre los candidatos contrastando **tres planos**:

- 📋 **Plan de gobierno** (PDF oficial) — lo que *prometen*.
- 🎤 **Declaraciones** (transcripciones de entrevistas/debates de YouTube) — lo que *dicen*.
- 💬 **Opiniones** (comentarios de YouTube) — lo que *opina la gente*.

Corre **100 % local/offline** (Ollama + modelos abiertos). Lee `PLAN_NUEVO_ENFOQUE.md` para el porqué.

> Reddit quedó descartado: su API para desarrolladores ya no es práctica. Todo el corpus de redes sale de YouTube.

## Estado

- Los 5 planes están en `Planes/`, ya mapeados a su candidato (Keiko Fujimori, Roberto Sánchez, Ricardo Belmont, Rafael López Aliaga, Jorge Nieto).
- `config.py` ya tiene tu YouTube API key, el modelo (`qwen3:4b`, que entra en tu GPU de 4 GB) y la búsqueda automática de videos.

## Instalación

```bash
pip install -r requirements.txt
ollama pull qwen3:4b
```

## Interfaz web (recomendada — sin terminal)

```bash
pip install flask
python app.py        # luego abre http://127.0.0.1:5000 en tu navegador
```

Página de chat profesional: escribe la pregunta y responde con las 3 secciones y sus fuentes.

## Diagnóstico de transcripciones

Si las transcripciones dan 0, corre esto para saber por qué (no instalada / IP bloqueada / sin subtítulos):

```bash
pip install youtube-transcript-api
python probar_transcript.py
```

## Uso (en orden)

```bash
# 1) Recolecta de YouTube: comentarios -> data/opiniones.jsonl
#    y transcripciones -> data/declaraciones.jsonl
python colectar_opiniones.py

# 2) Construye el índice con las 3 colecciones (oficial / declaracion / opinion)
python construir_indice.py

# 3) Chatea (respuestas en 3 secciones, con fuentes)
python chatbot.py
```

`colectar_opiniones.py` descubre los videos por candidato y de ahí saca comentarios y
transcripciones. Puedes limitarlo con `--solo comentarios` o `--solo transcripciones`
(ojo: cada archivo se reescribe por separado, así que para tener ambos corre el comando completo).

## Ajustes en `config.py`

- Volumen: `MAX_VIDEOS_POR_CANDIDATO`, `MAX_COMENTARIOS_POR_VIDEO`, `YOUTUBE_QUERY_SUFFIXES`.
- GPU: `OLLAMA_NUM_GPU = None` (auto), `0` (CPU), o un nº de capas (offload parcial). `OLLAMA_NUM_CTX` acota la VRAM.
- Recuperación: `TOP_K_RETRIEVE`, `TOP_K_RERANK`.

## Notas

- Las **transcripciones** dependen de que el video tenga subtítulos (la mayoría los tiene, auto-generados). Si YouTube llegara a bloquear la descarga desde tu IP, instala el respaldo: `pip install yt-dlp` (el script lo usa solo si la vía principal falla).
- Las **declaraciones** salen del video completo: en entrevistas es casi todo el candidato; en debates puede haber varios. El bot las presenta con cautela y cita el video.
- Las **opiniones** no son hechos verificados; el bot las marca como percepción.
- Si una pregunta no está en el corpus, el bot responde "No tengo esa información en mi corpus".
