"""
PLANTILLA de configuración. Cópiala a config.py y pon tu YOUTUBE_API_KEY:

    copy config.example.py config.py      (Windows)
    cp   config.example.py config.py      (Linux/Mac)

config.py está en .gitignore para no subir claves al repositorio.
"""
from pathlib import Path
import os

# --------------------------------------------------------------------------- #
# Rutas
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).parent
PDF_DIR = BASE_DIR / "Planes"              # los 5 planes de gobierno
DATA_DIR = BASE_DIR / "data"
OPINIONS_FILE = DATA_DIR / "opiniones.jsonl"           # comentarios (opinión)
DECLARACIONES_FILE = DATA_DIR / "declaraciones.jsonl"  # transcripciones de videos (declaraciones)
CHROMA_DIR = BASE_DIR / "chroma_db"        # índice vectorial persistente

# --------------------------------------------------------------------------- #
# Modelos (todos corren LOCAL/OFFLINE tras la primera descarga)
# --------------------------------------------------------------------------- #
EMBEDDING_MODEL = "BAAI/bge-m3"                  # embeddings multilingües
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"       # reordena por relevancia real
OLLAMA_MODEL = "qwen2.5:3b"                       # SIN modo 'thinking': rápido y directo, entra en 4 GB. (Alt: "qwen3:4b")
OLLAMA_NUM_GPU = None   # None = usar GPU (auto). 0 = forzar CPU. Un nº = capas a GPU (offload parcial).
OLLAMA_NUM_CTX = 4096   # ventana de contexto; 4096 va justo para 4 GB de VRAM (súbelo si tienes más)
OLLAMA_NUM_PREDICT = 1024   # largo máx. de la respuesta (más alto = respuestas más detalladas)

# --------------------------------------------------------------------------- #
# Parámetros de chunking y recuperación
# --------------------------------------------------------------------------- #
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
TOP_K_RETRIEVE = 12
TOP_K_RERANK = 5
MIN_OPINION_LEN = 40

# --------------------------------------------------------------------------- #
# Recolección de YouTube — el colector BUSCA los videos solo (no hace falta IDs)
# --------------------------------------------------------------------------- #
YOUTUBE_QUERY_SUFFIXES = ["entrevista", "debate", "propuestas"]
MAX_VIDEOS_POR_CANDIDATO = 10
MAX_COMENTARIOS_POR_VIDEO = 300
YOUTUBE_REGION = "PE"
YOUTUBE_LANG = "es"
YOUTUBE_PUBLICADO_DESPUES = "2025-06-01T00:00:00Z"
TRANSCRIPT_LANGS = ["es", "es-419", "es-PE"]
DECLARACION_TITULO_MENCIONA = True

# --------------------------------------------------------------------------- #
# Candidatos (TOP 5) — mapeados a sus PDFs en Planes/
# --------------------------------------------------------------------------- #
CANDIDATOS = [
    {
        "nombre": "Keiko Fujimori",
        "partido": "Fuerza Popular",
        "pdf": "da4b943d-4344-4743-9362-a11ccf3054cb.pdf",
        "alias": ["keiko", "fujimori", "fuerza popular", "fujimorismo", "fujimorista", "señora k", "la k"],
        "youtube_videos": [],
        "reddit_queries": ["Keiko Fujimori", "Fuerza Popular"],
    },
    {
        "nombre": "Roberto Sánchez",
        "partido": "Juntos por el Perú",
        "pdf": "3dd0e649-061c-4f31-8c3f-7a0836b58bde.pdf",
        "alias": ["roberto sánchez", "sánchez", "sanchez", "juntos por el perú", "juntos por el peru"],
        "youtube_videos": [],
        "reddit_queries": ["Roberto Sánchez Juntos por el Perú"],
    },
    {
        "nombre": "Ricardo Belmont",
        "partido": "Partido Cívico Obras",
        "pdf": "5643db28-6dbd-4d35-b79e-30d20d3bed85.pdf",
        "alias": ["belmont", "cívico obras", "civico obras", "partido obras"],
        "youtube_videos": [],
        "reddit_queries": ["Ricardo Belmont", "Partido Obras"],
    },
    {
        "nombre": "Rafael López Aliaga",
        "partido": "Renovación Popular",
        "pdf": "2096b44a-f3b6-4c81-b03d-94fbfc9ac762.pdf",
        "alias": ["lópez aliaga", "lopez aliaga", "renovación popular", "renovacion popular", "porky", "rpa"],
        "youtube_videos": [],
        "reddit_queries": ["López Aliaga", "Renovación Popular"],
    },
    {
        "nombre": "Jorge Nieto",
        "partido": "Partido del Buen Gobierno",
        "pdf": "19bde703-f7f4-4715-92f3-b82e19bbe651.pdf",
        "alias": ["jorge nieto", "nieto", "buen gobierno"],
        "youtube_videos": [],
        "reddit_queries": ["Jorge Nieto", "Partido del Buen Gobierno"],
    },
]

SUBREDDITS = ["PERU", "RepublicaPeru"]

# --------------------------------------------------------------------------- #
# CLAVES DE API — pega tu clave entre las comillas o usa variables de entorno.
#   Cómo obtenerlas: ver GUIA_APIS.md
# --------------------------------------------------------------------------- #
YOUTUBE_API_KEY      = "" or os.getenv("YOUTUBE_API_KEY", "")        # <-- pega aquí tu YouTube Data API v3
REDDIT_CLIENT_ID     = "" or os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = "" or os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = "chatbot-electoral-pe2026 by u/tu_usuario"
