"""
Traducción español <-> quechua para el chatbot.

Usa deep-translator (GoogleTranslator), que llama al endpoint gratuito de Google
Translate, sin API key. Google añadió el quechua (código "qu") en 2022.

IMPORTANTE: esta es la ÚNICA parte del sistema que requiere conexión a internet.
Solo se activa cuando el usuario elige el idioma quechua en la interfaz; el resto
del pipeline (embeddings, reranker, Chroma, Ollama) sigue funcionando 100% local.
Si no hay red o falla la traducción, se devuelve el texto original como respaldo.
"""
from functools import lru_cache

try:
    from deep_translator import GoogleTranslator
    _DISPONIBLE = True
except ImportError:
    _DISPONIBLE = False

# Límite práctico del endpoint de Google (~5000 chars). Traducimos por líneas, que
# además preserva los encabezados (📋/🎤/💬) y los marcadores de cita [n].
_MAX = 4500


def disponible() -> bool:
    """True si la librería está instalada (no garantiza que haya red)."""
    return _DISPONIBLE


@lru_cache(maxsize=1024)
def _traducir_linea(linea: str, source: str, target: str) -> str:
    try:
        out = GoogleTranslator(source=source, target=target).translate(linea[:_MAX])
        return out if out else linea
    except Exception:
        return linea  # respaldo: texto original


def _traducir(texto: str, source: str, target: str) -> str:
    """Traduce respetando saltos de línea (formato + límites de longitud)."""
    if not _DISPONIBLE or not texto or not texto.strip():
        return texto
    partes = []
    for linea in texto.split("\n"):
        partes.append(_traducir_linea(linea, source, target) if linea.strip() else linea)
    return "\n".join(partes)


def a_espanol(texto: str) -> str:
    """Input del usuario (quechua o lo que sea) -> español, para que lo consuma el modelo."""
    return _traducir(texto, "auto", "es")


def a_quechua(texto: str) -> str:
    """Respuesta del modelo (español) -> quechua, para mostrarla al usuario."""
    return _traducir(texto, "es", "qu")
