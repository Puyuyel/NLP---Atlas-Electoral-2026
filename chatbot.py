"""
Chatbot electoral Perú 2026 — versión de terminal (usa el núcleo rag.py).
Para una interfaz gráfica usa:  python app.py

Requisitos: ollama corriendo + haber ejecutado construir_indice.py
Uso: python chatbot.py
"""
import sys

from rag import RAG


def main():
    print("Cargando modelos locales (la 1ª vez descarga pesos)...")
    rag = RAG()
    disponibles = rag.planos_disponibles()
    if not disponibles:
        print("No encuentro el índice. Corre primero: python construir_indice.py")
        sys.exit(1)

    print(f"\n✅ Chatbot listo. Planos disponibles: {', '.join(disponibles)}. Escribe tu pregunta (o 'salir').\n")
    while True:
        try:
            pregunta = input("👤 Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not pregunta:
            continue
        if pregunta.lower() in {"salir", "exit", "quit"}:
            break

        r = rag.responder(pregunta)
        print("\n🤖", r["answer"])
        if r["fuentes"]:
            print("\n📚 Fuentes:")
            for f in r["fuentes"]:
                print(f"  [{f['n']}] {f['tipo']} — {f['ref']}")
        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
