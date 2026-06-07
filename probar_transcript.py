"""
Diagnóstico de transcripciones. Dice EXACTAMENTE por qué fallan:
  - librería no instalada
  - YouTube bloqueó tu IP (PoToken)
  - el video no tiene subtítulos en español
  - o funciona (muestra una porción)

Uso:
  python probar_transcript.py               # busca un video del 1er candidato y lo prueba
  python probar_transcript.py VIDEO_ID      # prueba un video específico
"""
import sys

import config


def _primer_video():
    from googleapiclient.discovery import build
    yt = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
    q = f"{config.CANDIDATOS[0]['nombre']} entrevista"
    r = yt.search().list(part="snippet", q=q, type="video", maxResults=1,
                         regionCode=config.YOUTUBE_REGION,
                         relevanceLanguage=config.YOUTUBE_LANG).execute()
    it = r["items"][0]
    return it["id"]["videoId"], it["snippet"]["title"]


def main():
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("❌ 'youtube-transcript-api' NO está instalado.")
        print("   Solución:  pip install youtube-transcript-api")
        return

    vid = sys.argv[1] if len(sys.argv) > 1 else None
    titulo = ""
    if not vid:
        if not config.YOUTUBE_API_KEY:
            print("Pásame un VIDEO_ID:  python probar_transcript.py VIDEO_ID")
            return
        try:
            vid, titulo = _primer_video()
        except Exception as e:
            print("No pude buscar un video (revisa tu API key):", e)
            return

    print(f"Probando video: {vid}  {titulo}\n")
    try:
        ytt = YouTubeTranscriptApi()
        try:
            tl = ytt.list(vid)
            print("Transcripciones disponibles en el video:")
            for t in tl:
                tipo = "auto" if getattr(t, "is_generated", False) else "manual"
                print(f"   - {t.language_code} ({tipo})")
        except Exception as e:
            print(f"   (no pude listar idiomas: {type(e).__name__})")

        fetched = ytt.fetch(vid, languages=config.TRANSCRIPT_LANGS)
        txt = " ".join(getattr(s, "text", "") for s in fetched)
        print(f"\n✅ FUNCIONA — {len(txt)} caracteres. Muestra:")
        print("  ", txt[:300], "...")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)[:200]}")
        print("   · Si menciona IP / blocked / PoToken: instala el respaldo -> pip install yt-dlp")
        print("   · Si dice NoTranscriptFound: ese video no tiene subtítulos en español.")


if __name__ == "__main__":
    main()
