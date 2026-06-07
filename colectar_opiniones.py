"""
Recolección de datos de YouTube (Reddit quedó descartado por cambios en su API).
Descubre videos por candidato y de ahí saca DOS cosas:
  · COMENTARIOS     -> data/opiniones.jsonl     (source_type=opinion)     "lo que opina la gente"
  · TRANSCRIPCIONES -> data/declaraciones.jsonl (source_type=declaracion) "lo que declara el candidato"

Para las DECLARACIONES solo se usan videos cuyo TÍTULO mencione al candidato
(config.DECLARACION_TITULO_MENCIONA), para evitar videos donde otra persona habla de él.

Requisitos:
  pip install google-api-python-client youtube-transcript-api langdetect
  (respaldo opcional de transcripciones) pip install yt-dlp

Uso:
  python colectar_opiniones.py                     # comentarios + transcripciones
  python colectar_opiniones.py --solo comentarios
  python colectar_opiniones.py --solo transcripciones
"""
import argparse
import json
import sys
from collections import Counter

import config
from utils_limpieza import (
    limpiar_texto, limpiar_transcript, menciona_candidato,
    opinion_valida, texto_util, chunk_texto,
)


def _registro(texto, candidato, source_type, plataforma, url, fecha="", titulo="", autor="", likes=0):
    return {
        "text": texto, "source_type": source_type, "platform": plataforma,
        "candidate": candidato, "url": url, "date": fecha, "title": titulo,
        "author": autor, "likes": likes,
    }


def _alias(cand):
    return next((c["alias"] for c in config.CANDIDATOS if c["nombre"] == cand), [])


# --------------------------------------------------------------------------- #
# Descubrir videos (YouTube Data API)
# --------------------------------------------------------------------------- #
def _build_yt():
    if not config.YOUTUBE_API_KEY:
        print("[YouTube] Falta YOUTUBE_API_KEY (ver GUIA_APIS.md).")
        return None
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("[YouTube] Instala google-api-python-client.")
        return None
    return build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)


def _buscar_videos(yt, query, n):
    params = dict(
        part="snippet", q=query, type="video", maxResults=min(n, 50),
        order="relevance", relevanceLanguage=config.YOUTUBE_LANG,
        regionCode=config.YOUTUBE_REGION,
    )
    if config.YOUTUBE_PUBLICADO_DESPUES:
        params["publishedAfter"] = config.YOUTUBE_PUBLICADO_DESPUES
    try:
        resp = yt.search().list(**params).execute()
    except Exception as e:
        print(f"[YouTube] búsqueda '{query}': {e}")
        return []
    return [
        (it["id"]["videoId"], it["snippet"].get("title", ""))
        for it in resp.get("items", []) if it["id"].get("videoId")
    ]


def descubrir_videos(yt):
    """{candidato: [(video_id, titulo), ...]} buscando nombre + cada sufijo."""
    mapa = {}
    for cand in config.CANDIDATOS:
        videos = {}
        for suf in config.YOUTUBE_QUERY_SUFFIXES:
            for vid, titulo in _buscar_videos(yt, f"{cand['nombre']} {suf}", config.MAX_VIDEOS_POR_CANDIDATO):
                videos.setdefault(vid, titulo)
        for vid in cand.get("youtube_videos", []):
            if vid and not vid.startswith("VIDEO_ID"):
                videos.setdefault(vid, "(manual)")
        mapa[cand["nombre"]] = list(videos.items())[: config.MAX_VIDEOS_POR_CANDIDATO]
        print(f"[Videos] {cand['nombre']}: {len(mapa[cand['nombre']])}")
    return mapa


# --------------------------------------------------------------------------- #
# Comentarios (opinión)
# --------------------------------------------------------------------------- #
def colectar_comentarios(yt, mapa):
    registros = []
    for cand, videos in mapa.items():
        for vid, titulo in videos:
            traidos, page = 0, None
            while traidos < config.MAX_COMENTARIOS_POR_VIDEO:
                try:
                    resp = yt.commentThreads().list(
                        part="snippet", videoId=vid, maxResults=100,
                        order="relevance", textFormat="plainText", pageToken=page,
                    ).execute()
                except Exception:
                    break
                for item in resp.get("items", []):
                    s = item["snippet"]["topLevelComment"]["snippet"]
                    registros.append(_registro(
                        texto=limpiar_texto(s.get("textDisplay", "")),
                        candidato=cand, source_type="opinion", plataforma="youtube",
                        url=f"https://www.youtube.com/watch?v={vid}",
                        fecha=s.get("publishedAt", ""), titulo=titulo,
                        autor=s.get("authorDisplayName", ""), likes=s.get("likeCount", 0),
                    ))
                    traidos += 1
                page = resp.get("nextPageToken")
                if not page:
                    break
        print(f"[Comentarios] {cand}: acumulado {len(registros)}")
    return registros


# --------------------------------------------------------------------------- #
# Transcripciones (declaraciones)
# --------------------------------------------------------------------------- #
def _transcript(vid):
    """Devuelve (texto, motivo). motivo='' si OK; si falla, explica por qué."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return "", "youtube-transcript-api NO instalado"
    try:
        try:
            fetched = YouTubeTranscriptApi().fetch(vid, languages=config.TRANSCRIPT_LANGS)
            return " ".join(getattr(s, "text", "") for s in fetched), ""
        except AttributeError:
            # versión antigua de la librería
            segs = YouTubeTranscriptApi.get_transcript(vid, languages=config.TRANSCRIPT_LANGS)
            return " ".join(s["text"] for s in segs), ""
    except Exception as e:
        txt = _transcript_ytdlp(vid)            # respaldo
        if txt:
            return txt, ""
        return "", type(e).__name__


def _transcript_ytdlp(vid):
    import glob
    import os
    import re
    import shutil
    import subprocess
    import tempfile
    if not shutil.which("yt-dlp"):
        return ""
    lang = config.TRANSCRIPT_LANGS[0]
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(
                ["yt-dlp", "--skip-download", "--write-auto-subs", "--write-subs",
                 "--sub-langs", lang, "--sub-format", "vtt",
                 "-o", os.path.join(tmp, "%(id)s"),
                 f"https://www.youtube.com/watch?v={vid}"],
                capture_output=True, timeout=120,
            )
        except Exception:
            return ""
        partes = []
        for f in glob.glob(os.path.join(tmp, "*.vtt")):
            for line in open(f, encoding="utf-8"):
                line = line.strip()
                if not line or "-->" in line or line.isdigit() or line.startswith("WEBVTT"):
                    continue
                partes.append(re.sub(r"<[^>]+>", "", line))
        return " ".join(partes)


def colectar_transcripciones(mapa):
    registros, con, motivos = [], 0, Counter()
    for cand, videos in mapa.items():
        alias = _alias(cand)
        for vid, titulo in videos:
            # relevancia: el título debe mencionar al candidato (evita "otro habla de X")
            if config.DECLARACION_TITULO_MENCIONA and titulo != "(manual)" and not menciona_candidato(titulo, alias):
                motivos["título no menciona al candidato"] += 1
                continue
            texto, motivo = _transcript(vid)
            texto = limpiar_transcript(texto)
            if not texto:
                motivos[motivo or "vacío"] += 1
                continue
            con += 1
            for chunk in chunk_texto(texto, config.CHUNK_SIZE, config.CHUNK_OVERLAP):
                registros.append(_registro(
                    texto=chunk, candidato=cand, source_type="declaracion",
                    plataforma="youtube_transcript",
                    url=f"https://www.youtube.com/watch?v={vid}", titulo=titulo,
                ))
        print(f"[Transcripciones] {cand}: {len(registros)} fragmentos acumulados")
    print(f"[Transcripciones] videos con transcripción: {con}")
    if motivos:
        print("[Transcripciones] descartes por motivo:")
        for m, c in motivos.most_common():
            print(f"    {c:4d}  {m}")
        if any("NO instalado" in m for m in motivos):
            print("    -> Corre: pip install youtube-transcript-api")
        if any(m in ("IpBlocked", "RequestBlocked", "YouTubeRequestFailed") for m in motivos):
            print("    -> YouTube bloqueó tu IP. Respaldo: pip install yt-dlp")
    return registros


# --------------------------------------------------------------------------- #
# Guardado (con filtros y dedup)
# --------------------------------------------------------------------------- #
def guardar(registros, ruta, es_opinion):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    vistos, n = set(), 0
    with open(ruta, "w", encoding="utf-8") as f:
        for r in registros:
            t = r["text"]
            if es_opinion:
                if not opinion_valida(t, config.MIN_OPINION_LEN, _alias(r["candidate"])):
                    continue
            elif not texto_util(t, config.MIN_OPINION_LEN):
                continue
            clave = t.lower()[:120]
            if clave in vistos:
                continue
            vistos.add(clave)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    print(f"✅ {n} registros guardados en {ruta}")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", choices=["comentarios", "transcripciones"], default=None)
    args = ap.parse_args()

    yt = _build_yt()
    if yt is None:
        sys.exit(1)
    mapa = descubrir_videos(yt)

    total = 0
    if args.solo in (None, "comentarios"):
        total += guardar(colectar_comentarios(yt, mapa), config.OPINIONS_FILE, es_opinion=True)
    if args.solo in (None, "transcripciones"):
        total += guardar(colectar_transcripciones(mapa), config.DECLARACIONES_FILE, es_opinion=False)

    if total == 0:
        print("\nNo se guardó nada. Revisa la API key, la conexión o si los videos tienen transcripción.")


if __name__ == "__main__":
    main()
