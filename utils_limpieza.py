"""
Utilidades de limpieza y normalización de texto.
Se usan para PDFs (oficial), transcripciones (declaraciones) y comentarios (opinión).
"""
import re
import unicodedata

try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0  # resultados deterministas
    _HAS_LANGDETECT = True
except ImportError:
    _HAS_LANGDETECT = False

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")
MULTISPACE_RE = re.compile(r"\s+")
TAG_RE = re.compile(r"\[[^\]]*\]")            # [Música], [Aplausos]… (subtítulos)
PAREN_TAG_RE = re.compile(r"\((?:risas|aplausos|m[uú]sica)\)", re.IGNORECASE)
TIMESTAMP_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")   # 1:23 o 01:02:03
ELONG_RE = re.compile(r"(.)\1{2,}", re.DOTALL)              # holaaaa -> holaa
EMOJI_RE = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U00002600-\U000027BF" "\U0001F1E6-\U0001F1FF" "]+",
    flags=re.UNICODE,
)


def colapsar_elongaciones(texto: str) -> str:
    """Reduce repeticiones de 3+ a 2: 'siiii'->'sii', 'jajajaja'->'jaja', '!!!'->'!!'."""
    return ELONG_RE.sub(r"\1\1", texto)


def limpiar_texto(texto: str, quitar_emojis: bool = True) -> str:
    """Limpieza estándar para comentarios y texto de planes."""
    if not texto:
        return ""
    texto = URL_RE.sub(" ", texto)
    texto = MENTION_RE.sub(" ", texto)
    texto = HASHTAG_RE.sub(r"\1", texto)      # #Keiko -> Keiko
    texto = TAG_RE.sub(" ", texto)
    texto = PAREN_TAG_RE.sub(" ", texto)
    if quitar_emojis:
        texto = EMOJI_RE.sub(" ", texto)
    texto = colapsar_elongaciones(texto)
    texto = unicodedata.normalize("NFC", texto)
    texto = MULTISPACE_RE.sub(" ", texto).strip()
    return texto


def limpiar_transcript(texto: str) -> str:
    """Limpieza específica para transcripciones de video (subtítulos)."""
    if not texto:
        return ""
    texto = TAG_RE.sub(" ", texto)
    texto = PAREN_TAG_RE.sub(" ", texto)
    texto = TIMESTAMP_RE.sub(" ", texto)
    texto = URL_RE.sub(" ", texto)
    texto = colapsar_elongaciones(texto)
    texto = unicodedata.normalize("NFC", texto)
    texto = MULTISPACE_RE.sub(" ", texto).strip()
    return texto


def es_espanol(texto: str) -> bool:
    """True si el texto parece estar en español. Si no hay langdetect, no filtra."""
    if not _HAS_LANGDETECT:
        return True
    try:
        return detect(texto) == "es"
    except Exception:
        return False


def menciona_candidato(texto: str, alias) -> bool:
    """True si el texto menciona alguno de los alias del candidato."""
    t = texto.lower()
    return any(a.lower() in t for a in alias)


def proporcion_alfabetica(texto: str) -> float:
    """Fracción de caracteres que son letras o espacios (para descartar spam de símbolos)."""
    if not texto:
        return 0.0
    ok = sum(c.isalpha() or c.isspace() for c in texto)
    return ok / len(texto)


def opinion_valida(texto: str, min_len: int, alias=None) -> bool:
    """Filtro de calidad para un comentario: largo, varias palabras, español y (opcional) tema."""
    if len(texto) < min_len:
        return False
    if len(texto.split()) < 4:                 # al menos 4 palabras
        return False
    if proporcion_alfabetica(texto) < 0.5:     # descarta spam de símbolos/números
        return False
    if not es_espanol(texto):
        return False
    if alias and not menciona_candidato(texto, alias):
        return False
    return True


def texto_util(texto: str, min_len: int) -> bool:
    """Filtro genérico (transcripciones): largo mínimo y suficiente texto real."""
    if len(texto) < min_len:
        return False
    if proporcion_alfabetica(texto) < 0.5:
        return False
    return True


def chunk_texto(texto: str, size: int, overlap: int):
    """Parte un texto largo en fragmentos con solape, respetando palabras."""
    palabras = texto.split()
    if not palabras:
        return []
    chunks, i = [], 0
    paso = max(1, (size - overlap) // 6)       # ~1 palabra ≈ 6 caracteres
    ventana = max(1, size // 6)
    while i < len(palabras):
        chunk = " ".join(palabras[i : i + ventana])
        if chunk.strip():
            chunks.append(chunk.strip())
        i += paso
    return chunks
