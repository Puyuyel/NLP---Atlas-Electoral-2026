"""
Diagnóstico del modelo: muestra si el 'thinking' se desactiva en TU equipo
y en qué campo viene el razonamiento. Robusto al objeto pydantic de ollama.

Uso:  python probar_modelo.py
"""
import ollama

import config

PREGUNTA = "En una sola frase, ¿qué es la seguridad ciudadana?"
MSGS = [{"role": "user", "content": PREGUNTA}]

print("Versión de ollama (python):", getattr(ollama, "__version__", "desconocida"))
print("Modelo:", config.OLLAMA_MODEL)


def _a_dict(msg):
    """El message de ollama es pydantic; lo pasamos a dict de forma segura."""
    for attr in ("model_dump", "dict"):
        f = getattr(msg, attr, None)
        if callable(f):
            try:
                return f()
            except Exception:
                pass
    if isinstance(msg, dict):
        return msg
    return {"content": getattr(msg, "content", "") or ""}


def info(r):
    d = _a_dict(r["message"])
    content = d.get("content") or ""
    thinking = d.get("thinking") or d.get("reasoning") or ""
    print("  campos del message:", list(d.keys()))
    print("  ¿campo 'thinking'/'reasoning'?:", bool(thinking), f"(len {len(thinking)})")
    print("  ¿'<think>' dentro de content?:", "<think>" in content)
    print("  content (300 chars):", repr(content[:300]))


def probar(think):
    etiqueta = "SIN parámetro think" if think is None else f"think={think}"
    try:
        if think is None:
            r = ollama.chat(model=config.OLLAMA_MODEL, messages=MSGS)
        else:
            r = ollama.chat(model=config.OLLAMA_MODEL, messages=MSGS, think=think)
    except TypeError as e:
        print(f"\n[{etiqueta}] ❌ tu 'ollama' de Python no soporta este parámetro -> pip install -U ollama ({e})")
        return
    except Exception as e:
        print(f"\n[{etiqueta}] error: {type(e).__name__}: {e}")
        print("   (si dice 'model not found', corre:  ollama pull " + config.OLLAMA_MODEL + ")")
        return
    print(f"\n=== {etiqueta} ===")
    info(r)


probar(False)   # lo que usa el chatbot: con qwen2.5 debe venir LIMPIO
probar(None)
print("\nLectura: con qwen2.5:3b el content debe salir limpio (sin <think> ni razonamiento).")
